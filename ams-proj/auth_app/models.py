from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField


class Faculty(models.Model):
    name = models.CharField(_("Faculty"), max_length=100)

    class Meta:
        verbose_name = _("Faculty")
        verbose_name_plural = _("Faculties")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class CustomUserManager(BaseUserManager):
    def _validate_required_fields(self, **fields: str) -> None:
        for field_name, value in fields.items():
            if not value:
                raise ValueError(_(f"{field_name.replace('_', ' ').title()} is required."))

    def create_user(
        self,
        first_name: str,
        last_name: str,
        school_email: str,
        gender: str,
        phone: str,
        password: str,
        email: str | None = None,
        faculty=None,
        profile_image=None,
        **extra_fields,
    ) -> "CustomUser":
        self._validate_required_fields(
            first_name=first_name,
            last_name=last_name,
            school_email=school_email,
            phone=phone,
            password=password,
            gender=gender,
        )

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            school_email=self.normalize_email(school_email),
            email=self.normalize_email(email) if email else None,
            gender=gender,
            phone=phone,
            faculty=faculty,
            profile_image=profile_image,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name: str, last_name: str, school_email: str, gender: str, phone: str, password: str, **extra_fields) -> "CustomUser":
        extra_fields.update({"is_active": True, "is_staff": True, "is_superuser": True})
        return self.create_user(first_name, last_name, school_email, gender, phone, password, **extra_fields)

    def create_admin(self, first_name: str, last_name: str, school_email: str, gender: str, phone: str, password: str, email: str, faculty, **extra_fields) -> "CustomUser":
        extra_fields.update({"is_active": True, "is_staff": True, "is_superuser": False})
        return self.create_user(first_name, last_name, school_email, gender, phone, password, email, faculty, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class GenderChoices(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")

    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(_("First Name"), max_length=50)
    last_name = models.CharField(_("Last Name"), max_length=50)
    school_email = models.EmailField(_("School Email"), max_length=254, unique=True)
    email = models.EmailField(_("Personal Email"), max_length=254, unique=True, null=True, blank=True)
    gender = models.CharField(_("Gender"), max_length=1, choices=GenderChoices.choices)
    phone = models.CharField(_("Phone"), max_length=20)
    faculty = models.ForeignKey(
        Faculty,
        verbose_name=_("Faculty"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    profile_image = CloudinaryField(
        "profile_image",
        folder="profile_images/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(_("Active"), default=True)
    is_staff = models.BooleanField(_("Staff Status"), default=False)
    date_joined = models.DateTimeField(_("Date Joined"), auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "school_email"
    REQUIRED_FIELDS = ["first_name", "last_name", "gender", "phone"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return self.get_full_name()

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name


class Student(models.Model):
    matricule = models.CharField(_("Matricule"), max_length=15, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Students")

    def __str__(self) -> str:
        return f"{self.user.get_full_name()} ({self.matricule})"


class Lecturer(models.Model):
    employee_id = models.CharField(_("Employee ID"), max_length=50, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="lecturer_profile",
    )

    class Meta:
        verbose_name = _("Lecturer")
        verbose_name_plural = _("Lecturers")

    def __str__(self) -> str:
        return f"{self.user.get_full_name()} ({self.employee_id})"


class Staff(models.Model):
    position = models.CharField(_("Position"), max_length=100)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )

    class Meta:
        verbose_name = _("Staff")
        verbose_name_plural = _("Staff")

    def __str__(self) -> str:
        return f"{self.user.get_full_name()} — {self.position}"