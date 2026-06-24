from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField


# Create your models here.

class Faculty(models.Model):
    name = models.CharField(_("Faculty"), max_length=10)

    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, school_email, gender, phone, password, email= None, faculty=None, profile_image=None, **extra_fields):

        if not first_name:
            raise ValueError("First name is required")
        if not last_name:
            raise ValueError("Last name is required")
        if not school_email:
            raise ValueError("Email is required")
        if not phone:
            raise ValueError("Phone is required")
        if not password:
            raise ValueError("Password is required")
        if not gender:
            raise ValueError("Gender is required")
        
        school_email = self.normalize_email(school_email)

        if email:
            email = self.normalize_email(email)

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            school_email=school_email,
            email=email,
            gender=gender,
            phone=phone,
            faculty= faculty,
            profile_image=profile_image,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, school_email, gender, phone, password, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(first_name, last_name, school_email, gender, phone, password, **extra_fields)
    
    def create_admin(self, first_name, last_name, school_email, gender, phone, password, email, faculty, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self.create_user(first_name, last_name, school_email, gender, phone, password, email, faculty, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female")
    ]
    
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=30)
    school_email = models.EmailField(_("School Email"), max_length=254, unique=True)
    email = models.EmailField(_("Email Address"), max_length=254, unique=True, null=True)
    gender = models.CharField(_("Gender"), max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20)
    faculty = models.ForeignKey(Faculty, verbose_name=_("Faculty"), on_delete=models.SET_NULL, null=True)
    profile_image = CloudinaryField(
        'profile_image',
        folder='profile_images/',
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "school_email"
    REQUIRED_FIELDS = ["first_name", "last_name", "email", "gender", "phone"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Student(models.Model):
    matricule = models.CharField(max_length=15, primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_(""), on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.user)
    
class Lecturer(models.Model):
    employee_id = models.CharField(max_length=50, primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_(""), on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class Staff(models.Model):
    position = models.CharField(max_length=100)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_(""), on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)
