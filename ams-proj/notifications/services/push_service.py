from notifications.models import Notification, DeviceToken
from firebase_admin import messaging


class PushService:

    @staticmethod
    def send(notification_id):

        notification = Notification.objects.select_related(
            "recipient"
        ).get(
            id=notification_id
        )

        devices = DeviceToken.objects.filter(
            user=notification.recipient,
            is_active=True,
        )

        if not devices.exists():
            return

        for device in devices:

            message = messaging.Message(
                token=device.token,

                notification=messaging.Notification(
                    title=notification.title,
                    body=notification.body,
                ),

                data={
                    "notification_id": str(
                        notification.id
                    ),
                    "type": notification.type,
                },
            )

            try:
                response = messaging.send(
                    message
                )

                print(
                    f"Sent: {response}"
                )

            except Exception as e:
                print(e)