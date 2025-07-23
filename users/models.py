from django.db import models
from django.contrib.auth.models import AbstractUser
from main.models import Course, Lesson

class User(AbstractUser):
    class Role(models.TextChoices):
        teacher = "TEACHER", "Teacher"
        student = "STUDENT", "Student"

    role = models.CharField(max_length=20,choices=Role.choices, default=Role.student)
    phone_number = models.CharField(max_length=13, null=True, blank=True)
    group = models.CharField(max_length=100, null=True, blank=True)
    course = models.ManyToManyField(Course)
    lesson = models.ManyToManyField(Lesson)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


