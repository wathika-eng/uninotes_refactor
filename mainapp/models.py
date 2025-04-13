import os
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


def note_file_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1]
    base_title = (instance.title or os.path.splitext(filename)[0])[:20]
    return os.path.join("media", f"{base_title}.{ext}")


class Course(models.Model):
    name = models.CharField(max_length=100)

    def get_display_name(self):
        return self.name.upper()
    
    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=100)
    course_name = models.CharField(max_length=100)
    year_of_study = models.CharField(max_length=20, null=True)
    sem = models.CharField(max_length=20, null=True)
    course = models.ForeignKey(Course, related_name="units", on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="units", null=True, blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_name.upper()}: {self.name} ({self.year_of_study}, Sem {self.sem})"

    class Meta:
        unique_together = [("name", "course_name", "year_of_study")]
        indexes = [models.Index(fields=["course"])]


class Note(models.Model):
    title = models.CharField(max_length=50, null=True, unique=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="notes")
    file = models.FileField(upload_to=note_file_path, unique=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.get_display_name()

    def get_display_name(self):
        filename = os.path.basename(self.file.name)
        base, _ = os.path.splitext(filename)
        return base[:20] 
    
    def save(self, *args, **kwargs):
        if not self.title:
            self.title = os.path.splitext(os.path.basename(self.file.name))[0][:20]
        self.file.name = note_file_path(self, self.file.name)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (
            ("title", "unit"),
            ("title", "file"),
            ("unit", "file"),
            ("title", "unit", "file"),
        )
        indexes = [models.Index(fields=["-uploaded_at"])]


class UserRequest(models.Model):
    yourschool = models.CharField(max_length=100, null=True)
    yourcourse = models.CharField(max_length=100, null=True)
    enquiry = models.TextField(blank=True)

    def __str__(self):
        return f"Request from {self.yourschool} - {self.yourcourse}"
