from django.urls.conf import path
from .views import SessionCreateView, SessionEndView


urlpatterns = [
    path("lecturer/create/", SessionCreateView.as_view(), name="Create Session"),
    path("lecturer/end/<uuid:session_id>/", SessionEndView.as_view(), name="End Session"),
]

