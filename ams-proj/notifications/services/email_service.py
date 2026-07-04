from django.core.mail import send_mail
from django.conf import settings

from notifications.models import Notification


class EmailService:

    @staticmethod
    def send(notification_id):

        notification = (
            Notification.objects
            .select_related("recipient")
            .get(id=notification_id)
        )

        user = notification.recipient

        if not user.email:
            return

        send_mail(
            subject=notification.title,
            message=notification.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )