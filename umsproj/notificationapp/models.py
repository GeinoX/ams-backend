from django.db import models
from django.conf import settings

# Create your models here.

class Notification(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_notifications")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # All students who should receive it
    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="notifications")

    # Students who already got it
    delivered = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="delivered_notifications", blank=True)

    def __str__(self):
        return f"{self.message[:30]}... from {self.sender.name}"