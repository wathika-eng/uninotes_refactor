from django.contrib import admin
from mainapp.models import Unit, Note, UserRequest, Course


class UnitAdmin(admin.ModelAdmin):
    list_filter = [
        "course_name",
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


class CourseAdmin(admin.ModelAdmin):
    list_display = ("name",)  # Fields to display in the admin list view
    search_fields = ("name",)  # Fields to enable searching in the admin
    list_filter = ("name",)  # Fields to filter by in the admin


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
