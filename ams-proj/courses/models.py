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