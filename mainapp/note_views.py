from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpRequest
from .models import Course, Unit, Note
from collections import defaultdict
from django.db.models import Count


# ---------- Helper Function ----------
def serialize_queryset(queryset, fields):
    return [{field: getattr(obj, field) for field in fields} for obj in queryset]


# ---------- Page Views ----------
def course_details(request: HttpRequest, course_id: int):
    course = get_object_or_404(Course, pk=course_id)
    units_with_notes = course.units.annotate(note_count=Count("notes")).filter(
        note_count__gt=0
    )

    units_by_year = defaultdict(list)
    for unit in units_with_notes:
        units_by_year[unit.year_of_study].append(unit)

    return render(
        request,
        "mainapp/course_details.html",
        {
            "course": course,
            "units_by_year": dict(units_by_year),
        },
    )


def unit_details(request: HttpRequest, unit_id: int):
    unit = get_object_or_404(Unit, pk=unit_id)
    notes = unit.notes.all()
    return render(request, "mainapp/unit_details.html", {"unit": unit, "notes": notes})


# ---------- API Endpoints ----------
def get_courses(request: HttpRequest):
    courses = Course.objects.all()
    data = [{"id": c.id, "name": c.get_display_name()} for c in courses]
    return JsonResponse(data, safe=False)


def get_units(request: HttpRequest):
    units = Unit.objects.filter(course_id=request.GET.get("course_id"))
    return JsonResponse(serialize_queryset(units, ["id", "name"]), safe=False)


# ---------- Upload View ----------
@login_required(login_url="login")
def submit_notes(request):
    if request.method == "POST":
        try:
            # Check if all necessary fields are in the request
            unit_id = request.POST.get("unit")
            if not unit_id:
                return JsonResponse({"success": False, "message": "Unit is required."})

            unit = get_object_or_404(Unit, pk=unit_id)

            uploaded_files = request.FILES.getlist("note_file")
            if not uploaded_files:
                return JsonResponse(
                    {"success": False, "message": "At least one file must be uploaded."}
                )

            # Loop through uploaded files and create Note objects
            for uploaded_file in uploaded_files:
                # Optional: Validate file type and size
                if uploaded_file.size > 10 * 1024 * 1024:  # Example: max file size 10MB
                    return JsonResponse(
                        {"success": False, "message": "File size exceeds limit (10MB)."}
                    )

                # Save the note
                Note.objects.create(
                    title=uploaded_file.name,
                    file=uploaded_file,
                    uploaded_by=request.user,
                    unit=unit,
                )

            # Return success response with the unit details page URL
            return JsonResponse(
                {"success": True, "message": f"/unit_details/{unit.id}"}
            )

        except Exception as e:
            # Catch any exceptions and return a detailed error message
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request method."})
