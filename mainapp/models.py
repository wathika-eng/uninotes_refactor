import os
from django.contrib.auth.models import User
from django.db import models


def note_file_path(instance, filename):
    # Generate the path where the file will be stored
    ext = filename.split(".")[-1]
    filename = f"{instance.title[:20]}.{ext}"  # Title shortened to 20 chars for uniqueness
    return os.path.join("media/", filename)


class Course(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name}"

    def get_display_name(self):
        return f"{self.name}"

class Unit(models.Model):
    name = models.CharField(max_length=100)
    course_name = models.CharField(max_length=100)  # Just storing the course name
    year_of_study = models.CharField(max_length=20, null=True)  # User-defined
    sem = models.CharField(max_length=20, null=True)
    course = models.ForeignKey(Course, related_name="units", on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="units", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course_name.upper()}: {self.name} ({self.year_of_study}, Sem {self.sem})"

    class Meta:
        unique_together = ["name", "course_name", "year_of_study"]


class Note(models.Model):
    title = models.CharField(max_length=50, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="notes")
    file = models.FileField(upload_to=note_file_path)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def get_display_name(self):
        # Get a cleaned up display name for the note
        filename = os.path.basename(self.file.name)
        base, ext = os.path.splitext(filename)
        return f"{base[:20]}{ext}"

    def __str__(self):
        return self.get_display_name()

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


class UserRequest(models.Model):
    yourschool = models.CharField(max_length=100, null=True)
    yourcourse = models.CharField(max_length=100, null=True)
    enquiry = models.TextField(blank=True)

    def __str__(self):
        return f"Request from {self.yourschool} - {self.yourcourse}"
