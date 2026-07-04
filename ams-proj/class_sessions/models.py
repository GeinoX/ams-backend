from django.db import models
import uuid


# Create your models here.

class Session(models.Model):
    session_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    course_offering = models.ForeignKey("courses.CourseOffering", on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course_offering.course.name} - Session {self.session_id}"

