from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('reports', views.GarbageReportViewSet, basename='garbage-reports')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.login, name='login'),
    path('send-otp/', views.send_otp, name='send-otp'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('unviewed-reports/', views.get_unviewed_reports_count, name='unviewed-reports'),
]




