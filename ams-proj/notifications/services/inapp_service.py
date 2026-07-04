from django.conf import settings

from notifications.models import Notification


class InappService:

    @staticmethod
    def send(notification_id):

        notification = (
            Notification.objects
            .select_related("recipient")
            .get(id=notification_id)
        )

   