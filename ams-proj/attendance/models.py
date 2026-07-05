from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog

# Create your models here.

class Attendance(models.Model):

    class AttendanceChoices(models.TextChoices):
        PRESENT = "Present", _("Present")
        ABSENT = "Absent", _("Absent")
        PENDING = "Pending", _("Pending")
        JUSTIFIED = "Justified", _("Justified")

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    student = models.ForeignKey("auth_app.Student", on_delete=models.SET_NULL, null=True)
    session = models.ForeignKey("class_sessions.Session", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=AttendanceChoices.choices, default=AttendanceChoices.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ["student", "session"]

    def __str__(self):
        student = self.student.user.get_full_name() if self.student else "Unknown"  # ← traverse to user
        return f"{student} - {self.session.course_offering.course.name}"


class PendingAttendance(models.Model):
    session = models.ForeignKey(
        "class_sessions.Session",
        on_delete=models.CASCADE,
        related_name='pending_attendances'
    )
    adder = models.ForeignKey(
        "auth_app.Student",
        on_delete=models.CASCADE,
        related_name='added_attendances',
        null=True,
        blank=True
    )
    added_student = models.ForeignKey(
        "auth_app.Student",
        on_delete=models.CASCADE,
        related_name='pending_attendances',
        null=True,
        blank=True
    )
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'added_student')

    def __str__(self):
        adder = self.adder.user.get_full_name() if self.adder else "Unknown"
        added_student = self.added_student.user.get_full_name() if self.added_student else "Unknown"
        return f"{added_student} pending in {self.session.course_offering.course.name} by {adder}"
    
auditlog.register(Attendance)
auditlog.register(PendingAttendance)