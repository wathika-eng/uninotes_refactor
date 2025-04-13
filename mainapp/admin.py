from django.contrib import admin
from django import forms
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from mainapp.models import Unit, Note, UserRequest, Course
import csv


class UnitAdmin(admin.ModelAdmin):
    list_filter = [
        "course",
        "year_of_study",
        "uploaded_by",
    ]  # Filtering by course_name instead of Course
    search_fields = [
        "name",
        "course_name",
        "year_of_study",
        "sem",
    ]  # Allow searching by unit name, course name, year, and semester
    date_hierarchy = "uploaded_at"  # Add date-based navigation in the admin panel


class NoteAdmin(admin.ModelAdmin):
    list_filter = [
        "unit",
        "uploaded_by",
        "status",
    ]  # Allow filtering by unit and status
    search_fields = [
        "title",
        "unit__name",
        "file",
    ]  # Search by note title, unit name, or file
    list_display = (
        "title",
        "unit",
        "uploaded_by",
        "uploaded_at",
        "status",
    )  # Display additional fields in the list


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()


from django.urls import re_path


class CourseAdmin(admin.ModelAdmin):
    list_display = ["name"]
    # change_list_template = "admin/courses_change_list.html"  # Optional custom template

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(
                r"^upload-csv/$",
                self.admin_site.admin_view(self.import_csv),
                name="courses_upload_csv",
            ),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    csv_file = request.FILES["csv_file"]
                    reader = csv.DictReader(
                        csv_file.read().decode("utf-8").splitlines()
                    )
                    count = 0
                    for row in reader:
                        course_name = row["Course Name"].strip()
                        if not Course.objects.filter(name__iexact=course_name).exists():
                            Course.objects.create(name=course_name)
                            count += 1
                    self.message_user(
                        request,
                        f"Successfully imported {count} courses",
                        messages.SUCCESS,
                    )
                except Exception as e:
                    self.message_user(
                        request, f"Error importing CSV: {e}", messages.ERROR
                    )
        else:
            form = CSVUploadForm()

        context = {
            "form": form,
            "opts": self.model._meta,
            "title": "Import CSV",
        }
        return render(request, "admin/csv_upload.html", context)

    def import_courses(self, request, queryset):
        from django.http import HttpResponseRedirect

        return HttpResponseRedirect("upload-csv/")

    import_courses.short_description = "Import courses from CSV"
    actions = [import_courses]


# @admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    list_display = (
        "yourschool",
        "yourcourse",
        "enquiry",
    )  # Fields to display in the admin list view
    search_fields = (
        "yourschool",
        "yourcourse",
        "enquiry",
    )  # Fields to enable searching in the admin
    list_filter = ("yourschool", "yourcourse")  # Fields to filter by in the admin


admin.site.register(Unit, UnitAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(UserRequest, UserRequestAdmin)
admin.site.register(Course, CourseAdmin)
