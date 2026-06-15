from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField
import uuid


# ==============================
# Custom User Manager
# ==============================
class CustomUserManager(BaseUserManager):
    def create_user(self, name, email, gender, phone, profile_image=None, password=None, **extra_fields):
        if not name:
            raise ValueError("Name is required")
        if not email:
            raise ValueError("Email is required")
        if not gender:
            raise ValueError("Gender is required")
        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)

        user = self.model(
            name=name,
            email=email,
            gender=gender,
            phone=phone,
            profile_image=profile_image,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, gender, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(name, email, gender, phone, password=password, **extra_fields)


# ==============================
# Custom User Model
# ==============================
class CustomUser(AbstractBaseUser, PermissionsMixin):

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=50, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.BigIntegerField(unique=True)
    profile_image = CloudinaryField(
        'profile_image',
        folder='profile_images/',
        blank=False,
        null=False
    )

    can_logout = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_teacher = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "gender", "phone"]

    def __str__(self):
        return self.name


# ==============================
# Student
# ==============================
class Student(models.Model):
    matricule = models.CharField(max_length=12, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )
    school_email = models.EmailField(unique=True)
    program = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return f"{self.user.name} - Student"

# ==============================
# Teacher
# ==============================
class Teacher(models.Model):
    employee_id = models.CharField(max_length=12, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile"
    )
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.name} - Teacher"


# ==============================
# Course
# ==============================
class Course(models.Model):
    LEVEL_CHOICES = [
        (100, "100 Level"),
        (200, "200 Level"),
        (300, "300 Level"),
        (400, "400 Level"),
    ]

    course_id = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    credits = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    level = models.IntegerField(choices=LEVEL_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_id} - {self.course_name}"


# ==============================
# Semester
# ==============================
class Semester(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            Semester.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.is_active and self.pk:
            active_count = Semester.objects.filter(is_active=True).exclude(pk=self.pk).count()
            if active_count == 0 and Semester.objects.count() == 1:
                raise ValidationError("Cannot deactivate the only semester in the system.")

    def delete(self, *args, **kwargs):
        if self.is_active and Semester.objects.filter(is_active=True).count() == 1:
            from django.core.exceptions import ValidationError
            raise ValidationError("Cannot delete the only active semester.")
        super().delete(*args, **kwargs)


# ==============================
# Course Offering
# ==============================
class CourseOffering(models.Model):
    course_offering_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="offerings"
    )
    semester = models.ForeignKey(Semester, on_delete=models.DO_NOTHING)
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.course_name} ({self.semester} {self.year})"


# ==============================
# Enrollment
# ==============================
class Enrollment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="student_enrollments"
    )
    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="course_enrollments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course_offering')

    def __str__(self):
        return f"{self.student.matricule} enrolled in {self.course_offering.course.course_id}"


# ==============================
# Session
# ==============================
class Session(models.Model):
    session_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course_offering.course.course_name} - Session {self.session_id}"


# ==============================
# Attendance
# ==============================
class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.matricule} - {self.session.session_id}"


# ==============================
# Course Assignment
# ==============================
class CourseAssignment(models.Model):
    lecturer = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="course_assignments"
    )
    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="course_assignments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('lecturer', 'course_offering')

    def __str__(self):
        return f"{self.lecturer.user.name} assigned to {self.course_offering.course.course_name}"


# ==============================
# Pending Attendance
# ==============================
class PendingAttendance(models.Model):
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='pending_attendances'
    )
    adder = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='added_attendances'
    )
    added_student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='pending_attendances'
    )
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'added_student')

    def __str__(self):
        return (
            f"{self.added_student.user.name} pending in "
            f"{self.session.course_offering.course.course_name} "
            f"by {self.adder.user.name}"
        )