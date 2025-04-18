import json
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django_daraja.mpesa.core import MpesaClient
from django.db.models import Prefetch
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import Note, Course, Unit, UserRequest


def health_check():
    return JsonResponse({"status": "ok"}, status=200)


def register(request):
    form = CreateUserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully")
        return redirect("login")
    return render(request, "mainapp/register.html", {"form": form})


def my_login(request):
    form = CustomAuthenticationForm(data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Logged in successfully")
            return redirect("dashboard")
        messages.warning(request, "Invalid username or password")
    return render(request, "mainapp/login.html", {"form": form})


def my_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("login")


def submit_request(request):
    if request.method == "POST":
        UserRequest.objects.create(
            yourschool=request.POST.get("yourschool"),
            yourcourse=request.POST.get("yourcourse"),
            enquiry=request.POST.get("enquiry"),
        )
        return redirect("dashboard")
    return render(request, "mainapp/modal.html")


# views.py
def dashboard(request):
    # Get all courses with optimized query
    all_courses = Course.objects.all().only("id", "name").order_by("name")

    # Get recent notes with optimized query
    recent_notes = Note.objects.select_related("unit", "unit__course").order_by(
        "-uploaded_at"
    )[:5]

    return render(
        request,
        "mainapp/dashboard.html",
        {
            "courses": all_courses,
            "notes": recent_notes,
            "courses_with_notes": set(
                Note.objects.values_list("unit__course_id", flat=True)
            ),
        },
    )


# @cache_page(60 * 15)  # Cache for 15 minutes
# def dashboard(request):
#     # Optimized query to get courses with notes and prefetch related data
#     courses_with_notes = (
#         Course.objects.filter(units__notes__isnull=False)
#         .distinct()
#         .prefetch_related(
#             Prefetch(
#                 "units",
#                 queryset=Unit.objects.annotate(notes_count=Count("notes"))
#                 .filter(notes_count__gt=0)
#                 .only("id", "name", "year_of_study", "sem"),
#             )
#         )
#         .only("id", "name")
#     )  # Only fetch fields we need

#     # Get recent notes with optimized query
#     recent_notes = Note.objects.select_related("unit", "unit__course").order_by(
#         "-uploaded_at"
#     )[:5]

#     return render(
#         request,
#         "mainapp/dashboard.html",
#         {"courses": courses_with_notes, "notes": recent_notes},
#     )


# def create_unit(request):
#     form = UnitForm(request.POST or None)
#     if request.method == "POST" and form.is_valid():
#         unit = form.save(commit=False)
#         unit.uploaded_by = request.user
#         unit.save()
#         return redirect("unit_list")
#     return render(request, "mainapp/unit_create.html", {"form": form})


# def send_password_reset_email(request):
#     user = User.objects.get(username="username")  # Replace with real user query
#     html_message = render_to_string("mainapp/registration/email/password_reset_email.html", {"user": user})
#     send_mail(
#         "Password Reset Request",
#         "",
#         "testkuku23@gmail.com",
#         [user.email],
#         html_message=html_message
#     )
#     return render(request, "mainapp/registration/password_reset_done.html")
class FileFieldFormView(FormView):
    form_class = NoteForm
    template_name = "mainapp/create_note.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        files = self.request.FILES.getlist("note_file")
        for f in files:
            # Check if the file already exists
            if Note.objects.filter(title=f.name).exists():
                messages.warning(self.request, f"File '{f.name}' already exists.")
                return JsonResponse(
                    {"success": False, "message": f"File '{f.name}' already exists"}
                )
            # Create the note
            Note.objects.create(
                file=f, uploaded_by=self.request.user, unit=form.cleaned_data["unit"]
            )

        # Show success message
        messages.success(self.request, "Files uploaded successfully.")

        # Return the regular response
        return super().form_valid(form)


@login_required(login_url="login")
def create_record(request):
    form = NoteForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        # Instantiate and use the FormView to handle the form
        view = FileFieldFormView()
        view.request = request
        response = view.form_valid(form)

        # If the response is a JSON response (AJAX), return it directly
        if isinstance(response, JsonResponse):
            return response

        # Redirect to the dashboard after successful form submission
        return redirect("dashboard")

    context = {
        "form": form,
        "courses": Course.objects.all(),
        "units": Unit.objects.all(),
        "notes": Note.objects.select_related(
            "college", "school", "department", "course", "unit"
        ),
    }
    return render(request, "mainapp/create_notes.html", context)


def mpesa(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        try:
            amount = int(request.POST.get("amount"))
        except ValueError:
            return HttpResponse("Invalid amount. Please enter a valid integer.")

        client = MpesaClient()
        response = client.stk_push(
            phone_number,
            amount,
            "reference",
            "Payment for services",
            settings.MPESA_CALLBACK_URL,
        )

        # Try extracting status safely
        try:
            # Try to convert response to dict
            response_data = response.json() if hasattr(response, 'json') else response.__dict__
            status = response_data.get("status", "failed")
        except Exception as e:
            print("MPESA error:", e)
            status = "failed"

        # Store status in session to check later
        request.session["payment_success"] = status == "success"

        context = {
            "previous_url": request.META.get("HTTP_REFERER"),
            "success_message" if status == "success" else "error_message":
                "Payment initiated successfully!" if status == "success" else "Payment initiation failed. Please try again.",
        }
        return render(request, "mainapp/money.html", context)

    return render(request, "mainapp/money.html")

@csrf_exempt
def check_payment_status(request):
    # If you're storing status in session
    success = request.session.get("payment_success", False)
    return JsonResponse({"success": success})

@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Optional: Log or store payment info
        print("Callback data:", data)

        # Here you can check `data['Body']['stkCallback']['ResultCode']` for success/failure
        try:
            result_code = data["Body"]["stkCallback"]["ResultCode"]
            result_desc = data["Body"]["stkCallback"]["ResultDesc"]

            success = result_code == 0
            # Save to DB or mark session/payment accordingly

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
        except KeyError:
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Failed to parse callback"})
    return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid method"})


def error_404_view(request, exception):
    return redirect("dashboard")


def sitemap(request):
    return render(request, "sitemap.xml")


def robots(request):
    return render(request, "robots.txt")

