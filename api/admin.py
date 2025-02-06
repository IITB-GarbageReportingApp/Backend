from django.contrib import admin


from django.contrib import admin

from api.models import GarbageReport, WorkerProfile

@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'zone', 'is_worker')
    list_filter = ('zone', 'is_worker')
    search_fields = ('user__username', 'user__email')

@admin.register(GarbageReport)
class GarbageReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'zone', 'status', 'reported_at', 'assigned_worker')
    list_filter = ('status', 'zone', 'reported_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('reported_at', 'completed_at')
# Register your models here.
