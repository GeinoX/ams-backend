from django.db import models
import uuid
from django.conf import settings


# Create your models here.

class NotificationType(models.TextChoices):
    # Attendance
    MARKED_ABSENT = "MARKED_ABSENT", "Marked Absent"
    MARKED_PRESENT = "MARKED_PRESENT", "Marked Present"
    MARKED_PENDING = "MARKED_PENDING", "Marked Pending"
    ATTENDANCE_JUSTIFIED = "ATTENDANCE_JUSTIFIED", "Attendance Justified"

    # Sessions
    SESSION_STARTED = "SESSION_STARTED", "Session Started"
    SESSION_ENDED = "SESSION_ENDED", "Session Ended"

    # Courses
    COURSE_CREATED = "COURSE_CREATED", "Course Created"
    COURSE_UPDATED = "COURSE_UPDATED", "Course Updated"
    COURSE_DELETED = "COURSE_DELETED", "Course Deleted"

    # Course Offering
    COURSE_OFFERING_CREATED = "COURSE_OFFERING_CREATED", "Course Offering Created"
    COURSE_OFFERING_UPDATED = "COURSE_OFFERING_UPDATED", "Course Offering Updated"
    COURSE_OFFERING_DELETED = "COURSE_OFFERING_DELETED", "Course Offering Deleted"

    # Enrollment
    ENROLLMENT_CREATED = "ENROLLMENT_CREATED", "Enrolled in Course"
    ENROLLMENT_DELETED = "ENROLLMENT_DELETED", "Removed from Course"

    # Assignment
    ASSIGNMENT_CREATED = "ASSIGNMENT_CREATED", "Assigned to Course"
    ASSIGNMENT_DELETED = "ASSIGNMENT_DELETED", "Removed from Course Assignment"

    # Auth
    REGISTERED = "REGISTERED", "Registered Successfully"
    PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"
    PASSWORD_CHANGED = "PASSWORD_CHANGED", "Password Changed"

    # General
    GENERAL = "GENERAL", "General"
    ANNOUNCEMENT = "ANNOUNCEMENT", "Announcement"
    REMINDER = "REMINDER", "Reminder"


class Notification(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")

    title = models.CharField(max_length=255)

    body = models.TextField()

    type = models.CharField(max_length=50, choices=NotificationType.choices, default=NotificationType.GENERAL)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} - {self.title}"
    

class DeviceToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="device_token")

    token = models.TextField(unique=True)

    ip_address = models.CharField(max_length=10, blank=True)

    platform = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    last_used_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.token[:20]}"