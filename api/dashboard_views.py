from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, F, Q
from django.utils import timezone
from django.db.models.functions import TruncDay
from datetime import timedelta, datetime
import json

from api.models import GarbageReport, WorkerProfile
from api.serializers import GarbageReportSerializer

@login_required
def dashboard(request):
    """
    Main dashboard view for all users
    """
    # Get all workers for the dropdown filter
    all_workers = WorkerProfile.objects.all()
    
    # Check if a specific worker is selected in the filter
    selected_worker_id = request.GET.get('worker_id')
    
    # Get all reports (optionally filter by worker)
    try:
        # Check if the current user is a worker
        worker_profile = WorkerProfile.objects.get(user=request.user)
        
        # If a worker is viewing their own dashboard, default to their reports
        if selected_worker_id:
            # Admin or user has selected a specific worker from dropdown
            selected_worker = get_object_or_404(WorkerProfile, id=selected_worker_id)
            reports = GarbageReport.objects.filter(assigned_worker=selected_worker).order_by('-reported_at')
            stats = calculate_dashboard_stats(selected_worker)
            weekly_labels, weekly_data = get_weekly_data(selected_worker)
        else:
            # Default to current worker's reports
            reports = GarbageReport.objects.filter(assigned_worker=worker_profile).order_by('-reported_at')
            stats = calculate_dashboard_stats(worker_profile)
            weekly_labels, weekly_data = get_weekly_data(worker_profile)
            
    except WorkerProfile.DoesNotExist:
        # User is not a worker, show all reports or filtered by selected worker
        if selected_worker_id:
            selected_worker = get_object_or_404(WorkerProfile, id=selected_worker_id)
            reports = GarbageReport.objects.filter(assigned_worker=selected_worker).order_by('-reported_at')
            stats = calculate_dashboard_stats(selected_worker)
            weekly_labels, weekly_data = get_weekly_data(selected_worker)
        else:
            # If no worker selected, show aggregate stats for all reports
            reports = GarbageReport.objects.all().order_by('-reported_at')
            worker_profile = None
            
            # Calculate aggregate stats for all reports
            stats = calculate_aggregate_stats()
            weekly_labels, weekly_data = get_aggregate_weekly_data()
    
    # Get the current selected worker for the template
    current_worker = None
    if selected_worker_id:
        current_worker = get_object_or_404(WorkerProfile, id=selected_worker_id)
    
    context = {
        'reports': reports,
        'worker_profile': worker_profile if 'worker_profile' in locals() else None,
        'stats': stats,
        'weekly_labels': json.dumps(weekly_labels),
        'weekly_data': json.dumps(weekly_data),
        'all_workers': all_workers,
        'selected_worker': current_worker,
    }
    
    return render(request, 'dashboard.html', context)


def format_resolution_time(avg_resolution_time):
    """
    Format the average resolution time in an appropriate unit (minutes, hours, or days)
    """
    if not avg_resolution_time:
        return "N/A"
    
    total_seconds = avg_resolution_time.total_seconds()
    
    # Less than an hour, show in minutes
    if total_seconds < 3600:
        return f"{total_seconds / 60:.1f} minutes"
    # Less than a day, show in hours
    elif total_seconds < 86400:
        return f"{total_seconds / 3600:.1f} hours"
    # More than a day, show in days and hours
    else:
        days = total_seconds // 86400
        remaining_hours = (total_seconds % 86400) / 3600
        if remaining_hours > 0:
            return f"{days:.0f} days, {remaining_hours:.1f} hours"
        else:
            return f"{days:.1f} days"


@login_required
def report_detail(request, report_id):
    """
    Detailed view of a single report
    """
    # Allow any authenticated user to view reports
    report = get_object_or_404(GarbageReport, id=report_id)
    
    # Only mark as viewed if the user is the assigned worker
    try:
        worker_profile = WorkerProfile.objects.get(user=request.user)
        if report.assigned_worker == worker_profile and not report.is_viewed:
            report.is_viewed = True
            report.save()
    except WorkerProfile.DoesNotExist:
        worker_profile = None
        
    return render(request, 'report_detail.html', {
        'report': report,
        'worker_profile': worker_profile
    })

def calculate_dashboard_stats(worker_profile):
    """
    Calculate statistics for the dashboard for a specific worker
    """
    current_date = timezone.now()
    one_month_ago = current_date - timedelta(days=190)
    
    # Get all reports for this worker in the last month
    reports = GarbageReport.objects.filter(assigned_worker=worker_profile)

    
    # Count by status
    sent = reports.filter(status='SENT').count()
    received = reports.filter(status='RECEIVED').count()
    in_progress = reports.filter(status='IN_PROGRESS').count()
    completed = reports.filter(status='COMPLETED').count()
    closed = reports.filter(status='CLOSED').count()
    
    # Calculate average resolution time
    completed_reports = reports.filter(
        status='COMPLETED', 
        completed_at__isnull=False,
        reported_at__isnull=False
    )

    # Print resolution time for each completed report
    for report in completed_reports:
        resolution_time = report.completed_at - report.reported_at
        print(report.completed_at)
        print(f"Report ID: {report.id} | Resolution Time: {resolution_time}")
    
    if completed_reports.exists():
        # Calculate time difference between reported_at and completed_at
        avg_resolution_hours = completed_reports.annotate(
            resolution_time=F('completed_at') - F('reported_at')
        ).aggregate(
            avg_time=Avg('resolution_time')
        )['avg_time']
        
        avg_time = format_resolution_time(avg_resolution_hours)
    else:
        avg_time = "N/A"
    
    return {
        'sent': sent,
        'received': received,
        'in_progress': in_progress,
        'completed': completed,
        'closed': closed,
        'new': sent,  # For the stats card
        'avg_time': avg_time
    }


def calculate_aggregate_stats():
    """
    Calculate aggregate statistics for all reports
    """
    current_date = timezone.now()
    # one_month_ago = current_date - timedelta(days=30)
    
    # Get all reports in the last month
    reports = GarbageReport.objects.all()
    
    # Count by status
    sent = reports.filter(status='SENT').count()
    received = reports.filter(status='RECEIVED').count()
    in_progress = reports.filter(status='IN_PROGRESS').count()
    completed = reports.filter(status='COMPLETED').count()
    closed = reports.filter(status='CLOSED').count()

    
    # Calculate average resolution time
    completed_reports = reports.filter(
        status='COMPLETED', 
        completed_at__isnull=False
    )
    
    if completed_reports.exists():
        # Calculate time difference between reported_at and completed_at
        avg_resolution_hours = completed_reports.annotate(
            resolution_time=F('completed_at') - F('reported_at')
        ).aggregate(
            avg_time=Avg('resolution_time')
        )['avg_time']
        
        avg_time = format_resolution_time(avg_resolution_hours)
    else:
        avg_time = "N/A"
    
    return {
        'sent': sent,
        'received': received,
        'in_progress': in_progress,
        'completed': completed,
        'closed': closed,
        'new': sent,  # For the stats card
        'avg_time': avg_time
    }

def get_weekly_data(worker_profile):
    """
    Get data for the weekly trend chart for a specific worker
    """
    # Get date range for the last 7 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)
    
    # Query to get daily counts
    daily_counts = GarbageReport.objects.filter(
        assigned_worker=worker_profile,
        reported_at__date__gte=start_date,
        reported_at__date__lte=end_date
    ).annotate(
        day=TruncDay('reported_at')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Prepare data for chart
    labels = []
    data = []
    
    # Create a dictionary with all dates
    current_date = start_date
    date_counts = {}
    while current_date <= end_date:
        date_counts[current_date] = 0
        current_date += timedelta(days=1)
    
    # Fill in the counts from the query
    for item in daily_counts:
        date_counts[item['day'].date()] = item['count']
    
    # Convert to ordered lists for the chart
    for date, count in sorted(date_counts.items()):
        labels.append(date.strftime('%b %d'))
        data.append(count)
    
    return labels, data

def get_aggregate_weekly_data():
    """
    Get aggregate data for the weekly trend chart for all reports
    """
    # Get date range for the last 7 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)
    
    # Query to get daily counts
    daily_counts = GarbageReport.objects.filter(
        reported_at__date__gte=start_date,
        reported_at__date__lte=end_date
    ).annotate(
        day=TruncDay('reported_at')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Prepare data for chart
    labels = []
    data = []
    
    # Create a dictionary with all dates
    current_date = start_date
    date_counts = {}
    while current_date <= end_date:
        date_counts[current_date] = 0
        current_date += timedelta(days=1)
    
    # Fill in the counts from the query
    for item in daily_counts:
        date_counts[item['day'].date()] = item['count']
    
    # Convert to ordered lists for the chart
    for date, count in sorted(date_counts.items()):
        labels.append(date.strftime('%b %d'))
        data.append(count)
    
    return labels, data