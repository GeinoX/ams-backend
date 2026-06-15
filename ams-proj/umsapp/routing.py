# umsapp/routing.py
from django.urls import re_path
from .consumers import PendingAttendanceConsumer

websocket_urlpatterns = [
    re_path(r'ws/pending_attendance/(?P<session_id>[^/]+)/(?P<teacher_id>[^/]+)/$', PendingAttendanceConsumer.as_asgi()),
]