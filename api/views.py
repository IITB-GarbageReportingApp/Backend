from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import random
import time
from .models import GarbageReport, WorkerProfile
from .serializers import UserSerializer, GarbageReportSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone



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
        user_type = request.data.get('user_type', 'user')  # Default to 'user' if not specified
        
        if not email or not password:
            return Response({
                'error': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'No account found with this email'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify user type matches
        if user_type == 'worker':
            try:
                worker_profile = user.workerprofile
                if not worker_profile.is_worker:
                    return Response({
                        'error': 'This account is not authorized as a J.E.'
                    }, status=status.HTTP_403_FORBIDDEN)
            except WorkerProfile.DoesNotExist:
                return Response({
                    'error': 'This account is not authorized as a J.E.'
                }, status=status.HTTP_403_FORBIDDEN)
        
        user = authenticate(username=user.username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            response_data = {
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }
            
            # Add worker information if applicable
            if user_type == 'worker':
                response_data['user']['worker_profile'] = {
                    'zone': user.workerprofile.zone,
                    'is_worker': True
                }
            
            return Response(response_data, status=status.HTTP_200_OK)
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
    serializer_class = GarbageReportSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = GarbageReport.objects.none()  # Add this line to provide a default queryset

    def perform_create(self, serializer):
        # Set the user to the current authenticated user
        serializer.save(user=self.request.user)


    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            # For unauthenticated users, return all reports
            return GarbageReport.objects.all().select_related('user').order_by('-reported_at')
        
        # Check if user is a worker
        try:
            worker_profile = user.workerprofile
            if worker_profile.is_worker:
                # Workers see reports from their zone
                return GarbageReport.objects.filter(
                    assigned_worker=worker_profile
                ).select_related('user').order_by('-reported_at')
        except WorkerProfile.DoesNotExist:
            # Regular users see their own reports
            return GarbageReport.objects.filter(
                user=user
            ).select_related('user').order_by('-reported_at')

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        report = self.get_object()
        new_status = request.data.get('status')
        completion_image = request.FILES.get('completion_image')
        worker_notes = request.data.get('worker_notes')

        if new_status not in dict(GarbageReport.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate completion image for COMPLETED status
        if new_status == 'COMPLETED':
            if not completion_image:
                return Response(
                    {'error': 'Completion image is required to mark as completed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            report.completion_image = completion_image
            report.completed_at = timezone.now()

        report.status = new_status
        if worker_notes:
            report.worker_notes = worker_notes
        report.save()
        
        return Response(GarbageReportSerializer(report).data)

    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        report = self.get_object()
        report.is_viewed = True
        report.save()
        return Response({'status': 'success'})

    @action(detail=True, methods=['post'])
    def close_report(self, request, pk=None):
        report = self.get_object()
        
        # Only allow the report creator to close it
        if report.user != request.user:
            return Response(
                {'error': 'Not authorized to close this report'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        report.status = 'CLOSED'
        report.save()
        return Response(GarbageReportSerializer(report).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unviewed_reports_count(request):
    """Get count of unviewed reports for a worker"""
    try:
        worker_profile = request.user.workerprofile
        count = GarbageReport.objects.filter(
            assigned_worker=worker_profile,
            is_viewed=False,
            status='SENT'  # Only count reports with SENT status
        ).count()
        return Response({'count': count})
    except WorkerProfile.DoesNotExist:
        return Response(
            {'error': 'User is not a worker'},
            status=status.HTTP_403_FORBIDDEN
        )  

    
