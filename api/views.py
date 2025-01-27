from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import random
import time
from .models import GarbageReport
from .serializers import UserSerializer, GarbageReportSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['POST'])
def send_otp(request):
    try:
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=400)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered'}, status=400)
        
        otp = str(random.randint(100000, 999999))
        # Store OTP with timestamp
        request.session['otp_data'] = {
            'otp': otp,
            'email': email,
            'timestamp': time.time()
        }
        
        try:
            send_mail(
                'OTP for Garbage Reporting App',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email sending error: {str(e)}")
            return Response({'error': 'Failed to send email'}, status=500)
        
        return Response({'message': 'OTP sent successfully'})
    except Exception as e:
        print(f"General error: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=500)


@api_view(['POST'])
def login(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get username from email since Django's authenticate uses username
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'No account found with this email'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Authenticate user with username and password
        user = authenticate(username=user.username, password=password)
        
        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        return Response({
            'error': f'Login failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
def verify_otp(request):
    try:
        received_otp = request.data.get('otp')
        password = request.data.get('password')
        
        if not received_otp or not password:
            return Response({'error': 'OTP and password are required'}, status=400)
        
        # Get stored OTP data
        otp_data = request.session.get('otp_data')
        if not otp_data:
            return Response({'error': 'OTP expired or not found'}, status=400)
        
        stored_otp = otp_data.get('otp')
        stored_email = otp_data.get('stored_email')
        timestamp = otp_data.get('timestamp')
        
        # Check if OTP has expired (15 minutes validity)
        if time.time() - timestamp > 900:  # 900 seconds = 15 minutes
            del request.session['otp_data']
            return Response({'error': 'OTP has expired'}, status=400)
        
        if received_otp != stored_otp:
            return Response({'error': 'Invalid OTP'}, status=400)
        
        # Create new user
        try:
            user_data = {
                'username': stored_email.split('@')[0],
                'email': stored_email,
                'password': make_password(password)  # Hash the password
            }
            serializer = UserSerializer(data=user_data)
            if serializer.is_valid():
                serializer.save()
                # Clear the OTP data after successful verification
                del request.session['otp_data']
                return Response({'message': 'User registered successfully'})
            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({'error': f'Failed to create user: {str(e)}'}, status=400)
            
    except Exception as e:
        return Response({'error': f'Verification failed: {str(e)}'}, status=500)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_report_status(request, report_id):
    try:
        report = GarbageReport.objects.get(id=report_id)
        new_status = request.data.get('status')
        
        if new_status not in dict(GarbageReport.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        report.status = new_status
        report.save()
        
        serializer = GarbageReportSerializer(report)
        return Response(serializer.data)
        
    except GarbageReport.DoesNotExist:
        return Response(
            {'error': 'Report not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    

class GarbageReportViewSet(viewsets.ModelViewSet):
    queryset = GarbageReport.objects.all()
    serializer_class = GarbageReportSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return GarbageReport.objects.all().select_related('user').order_by('-reported_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    