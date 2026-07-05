# sessions/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Session

# sessions/tasks.py
@shared_task
def auto_end_expired_sessions():
    Session.objects.filter(
        active=True,
        start_time__lt=timezone.now() - timedelta(hours=3)
    ).update(active=False, end_time=timezone.now())