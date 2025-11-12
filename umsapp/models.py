from django.db import models 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

import uuid


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

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(name, email, gender, phone, password=password, **extra_fields)


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
    profile_image = models.TextField(blank=True, null=True) 

    can_logout = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_teacher = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "gender", "phone"]

    def __str__(self):
        return self.name


# from django.utils.html import format_html

class Student(models.Model):
    matricule = models.CharField(max_length=12, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile"
    )
    school_email = models.EmailField(unique=True)
    program = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.name} - Student"

"""
    def profile_image_tag(self):
        if self.user.profile_image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', self.user.profile_image.url)
        return "No Image"

    profile_image_tag.short_description = "Profile Image"
"""


class Teacher(models.Model):
    employee_id = models.CharField(max_length=12, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_profile"
    )


    def __str__(self):
        return f"{self.user.name} - Teacher"

class Course(models.Model):
    course_id = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    credits = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    STATUS_CHOICES = [
        ("required", "Required"),
        ("compulsory", "Compulsory"),
        ("elective", "Elective"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    LEVEL_CHOICES = [
        ("l1s1", "L1S1"),
        ("l1s2", "L1S2"),
        ("l2s1", "L2S1"),
        ("l2s2", "L2S2"),
        ("l3s1", "L3S1"),
        ("l3s2", "L3S2"),
        ("l4s1", "L4S1"),
        ("l4s2", "L4S2"),
    ]
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)

    def __str__(self):
        return f"{self.course_id} - {self.course_name}"

class Semester(models.Model):
    period = models.CharField(max_length=10, choices=[
        ("Fall", "Fall"),
        ("Spring", "Spring"),
        ("Summer", "Summer")
    ])
    year = models.IntegerField()
    status = models.CharField(max_length=10, choices=[
        ("Past", "Past"),
        ("Current", "Current")
    ])

    class Meta:
        unique_together = ('period', 'year') 

    def __str__(self):
        return f"{self.period} {self.year} ({self.status})"
    
    


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("enrolled", "Enrolled"),
        ("completed", "Completed"),
        ("dropped", "Dropped"),
        ("failed", "Failed"),
    ]

 
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="studen_enrollments"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_enrollments"
    )
    enrollment_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="enrolled")
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name="semester_enrollments")
    grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Optional: final grade for the course"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "course", "semester")
        ordering = ["-enrollment_date"]
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.student.matricule} - {self.course.course_id} ({self.status})"
    
    def __str__(self):
        return f"{self.semester.period} - {self.semester.year}"


class Timetable(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="timetable_entries")
    day = models.CharField(max_length=10, choices=[
        ("Mon","Monday"),
        ("Tue","Tuesday"),
        ("Wed","Wednesday"),
        ("Thu","Thursday"),
        ("Fri","Friday")
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    hall = models.CharField(max_length=20)
    
    class Meta:
        unique_together = ("course", "day", "start_time") 

    def __str__(self):
        return f"{self.course.course_id} on {self.day} from {self.start_time} to {self.end_time}"



class Session(models.Model): 
    session_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    teacher = models.ForeignKey(
        Teacher, 
        on_delete=models.CASCADE, 
        related_name="sessions"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course.course_name} - {self.teacher.user.name}"

class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'student')  # prevents double check-in


class CourseAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10)
    year = models.CharField(max_length=5)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher.user} - {self.course.course_name}"
    

class PendingAttendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="pending_attendance")
    adder = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="added_students")
    added_student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="added_to_sessions")
    timestamp = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('session', 'adder', 'added_student')
