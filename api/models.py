from django.db import models
from django.contrib.auth.models import User

class GarbageReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='garbage_reports/')
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.user.username} at {self.reported_at}"