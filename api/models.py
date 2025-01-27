# models.py - Update the existing GarbageReport model
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import json
import os

class GarbageReport(models.Model):
    STATUS_CHOICES = [
        ('SENT', 'Sent'),
        ('RECEIVED', 'Received'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='garbage_reports/')
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    reported_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SENT')
    zone = models.CharField(max_length=100, blank=True)

    def get_zone_email(self):
        """Get email address for the current zone from email.json"""
        try:
            # Get the zone number from the zone field (e.g., "Zone 5" -> 5)
            if not self.zone or self.zone == "Unknown Zone":
                return None
                
            zone_number = int(self.zone.split()[-1])
            
            # Load email configuration
            email_config_path = os.path.join(settings.BASE_DIR, 'api', 'email.json')
            with open(email_config_path, 'r') as f:
                config = json.load(f)
            
            # Find matching zone
            for zone in config['zones']:
                if zone['zone_number'] == zone_number:
                    return zone['email']
            
            return None
        except Exception as e:
            print(f"Error getting zone email: {str(e)}")
            return None

    def save(self, *args, **kwargs):
        if not self.zone:
            self.zone = self.determine_zone()
        super().save(*args, **kwargs)

    def point_in_polygon(self, point, polygon):
        """
        Determine if a point is inside a polygon using ray casting algorithm
        """
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def determine_zone(self):
        import json
        from django.conf import settings
        import os

        geojson_path = os.path.join(settings.BASE_DIR, 'zone.json')
        
        try:
            with open(geojson_path) as f:
                zones_data = json.load(f)

            point = (self.longitude, self.latitude)
            
            for feature in zones_data['features']:
                # Get the first polygon coordinates
                coordinates = feature['geometry']['coordinates'][0][0]
                
                if self.point_in_polygon(point, coordinates):
                    return f"Zone {feature['properties']['Zone_No']}"
                    
        except Exception as e:
            print(f"Error determining zone: {str(e)}")
            
        return "Unknown Zone"

    def __str__(self):
        return f"Report by {self.user.username} at {self.reported_at}"

@receiver(post_save, sender=GarbageReport)
def send_zone_notification(sender, instance, created, **kwargs):
    """Send email notification when a new report is created"""
    if created:  # Only send email when a new report is created
        try:
            zone_email = instance.get_zone_email()
            
            if zone_email:
                # Prepare email content
                subject = f'New Garbage Report in {instance.zone}'
                message = f"""
A new garbage report has been submitted in your zone.

Details:
- Reporter: {instance.user.username}
- Location: {instance.latitude}, {instance.longitude}
- Description: {instance.description}
- Reported at: {instance.reported_at}

Please take necessary action.
"""
                
                # Send email
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[zone_email],
                    fail_silently=False,
                )
                
        except Exception as e:
            print(f"Error sending zone notification: {str(e)}")