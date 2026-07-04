from celery import shared_task
from notifications.services.push_service import (
    PushService
)
from notifications.services.email_service import (
    EmailService
)
from notifications.services.inapp_service import (
    InappService
)


@shared_task
def test_task():
    print("Hello from Celery!")

    from celery import shared_task

@shared_task
def send_push_notification(
    notification_id
):
    PushService.send(
        notification_id
    )

@shared_task
def send_inapp_notification(
    notification_id
):
    InappService.send(
        notification_id
    )

@shared_task
def send_email_notification(
    notification_id
):
    EmailService.send(
        notification_id
    )