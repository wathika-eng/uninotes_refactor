from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
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
            unit_id = request.POST.get("unit")
            unit_name = request.POST.get("unit_name", "").strip()
            course_id = request.POST.get("course")
            year = request.POST.get("year_of_study")
            sem = request.POST.get("sem")
            print(f"Unit ID: {unit_id}, Unit Name: {unit_name}, Course ID: {course_id}")
            unit = None

            # Option 1: Use existing unit
            if unit_id:
                unit = get_object_or_404(Unit, pk=unit_id)

            # If unit_name and course_id are provided, create a new unit
            elif unit_name and course_id:
                course = get_object_or_404(Course, pk=course_id)
                unit, created = Unit.objects.get_or_create(
                    name=unit_name,
                    course=course,
                    year_of_study=year,
                    sem=sem,
                    defaults={"uploaded_by": request.user},
                )
            else:
                return JsonResponse(
                    {"success": False, "message": "Please select or type a unit name."}
                )

            uploaded_files = request.FILES.getlist("note_file")
            if not uploaded_files:
                return JsonResponse(
                    {"success": False, "message": "Please upload at least one file."}
                )

            for uploaded_file in uploaded_files:
                if uploaded_file.size > 20 * 1024 * 1024:
                    return JsonResponse(
                        {"success": False, "message": "File exceeds 10MB limit."}
                    )
                # cloudinary_response = cloudinary.uploader.upload(uploaded_file)

                # # Debugging output
                # print(f"Cloudinary Response: {cloudinary_response}")
                try:
                    note = Note.objects.create(
                        title=uploaded_file.name,
                        file=uploaded_file,
                        unit=unit,
                        uploaded_by=request.user,
                    )
                    # Debugging: Print the note that was just created
                    print(f"Note uploaded: {note}")
                    print(
                        f"Note details: {Note.objects.filter(title=uploaded_file.name)}"
                    )

                except IntegrityError as e:
                    print(f"Error uploading note: {e}")
                    return JsonResponse(
                        {"success": False, "message": f"Error: {str(e)}"}
                    )

            return JsonResponse(
                {"success": True, "message": f"/unit_details/{unit.id}"}
            )

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request method."})
