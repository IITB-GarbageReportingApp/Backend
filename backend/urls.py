from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import GarbageReportViewSet, send_otp, verify_otp, login
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'reports', GarbageReportViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/send-otp/', send_otp),
    path('api/verify-otp/', verify_otp),
    path('api/login/', login),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)