from django.urls.conf import path
from .views import SessionCreateView, SessionEndView


urlpatterns = [
    path("create/", SessionCreateView.as_view(), name="Create Session"),
    path("end/", SessionEndView.as_view(), name="End Session"),
    
]

