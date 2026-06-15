# umsapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PendingAttendance
from .utils import notify_teacher_pending_attendance


@receiver(post_save, sender=PendingAttendance)
def send_pending_attendance_notification(sender, instance, created, **kwargs):
    if created and not instance.approved:
        notify_teacher_pending_attendance(instance)