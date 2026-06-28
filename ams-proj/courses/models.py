from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _



# Create your models here.

class Course(models.Model):
    
    class LevelChoices(models.TextChoices):
        LEVEL_1 = "L1", _("Level 1")
        LEVEL_2 = "L2", _("Level 2")
        LEVEL_3 = "L3", _("Level 3")
        LEVEL_4 = "L4", _("Level 4")


    id = models.CharField(max_length=20, primary_key=True, 
                          validators=[RegexValidator(regex=r'^CRS-\d{3}$', 
                          message= "ID must follow the format CRS-001")])
    
    name = models.CharField(max_length=40, unique=True)
    credits = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    level = models.CharField(max_length=2, choices=LevelChoices.choices, default=LevelChoices.LEVEL_1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.level})"
    
    class Meta:
        ordering = ["level", "name"]

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


class CourseOffering(models.Model):

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="offerings")
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, related_name="course_offering" )
    year = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["course", "semester", "year"]

    def __str__(self):
        return f"{self.course.name} ({self.semester} {self.year})"
    
class CourseAssignment(models.Model):

    lecturer = models.ForeignKey('auth_app.Lecturer', on_delete=models.SET_NULL, null=True, related_name="course_assignments")
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name="course_assignments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["lecturer", "course_offering"]

    def __str__(self):
        lecturer = self.lecturer.employee_id if self.lecturer else "Unassigned"
        return f"{lecturer} assigned to {self.course_offering.course.name}"

class CourseEnrollment(models.Model):

    student = models.ForeignKey('auth_app.Student', on_delete=models.SET_NULL, null=True, related_name="course_enrollment")
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name="course_enrollment")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["student", "course_offering"]

    def __str__(self):
        student = self.student.matricule if self.student else "Unkwown"
        return f"{student} enrolled in {self.course_offering.course.name}"