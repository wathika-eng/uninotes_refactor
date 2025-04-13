from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import note_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("register", views.register, name="register"),
    path("logout", views.my_logout, name="mylogout"),
    path("dash", views.dashboard, name="dashboard"),
        path("healthz", views.health_check, name="health_check"),
    # path(
    #     "send-reset-email/",
    #     views.send_password_reset_email,
    #     name="send_password_reset_email",
    # ),
    path("upload_notes", views.create_record, name="create_record"),
    # path("unit", views.create_unit, name="unit"),
    path("submit_request/", views.submit_request, name="submit_request"),
    path("get_courses/", note_views.get_courses, name="get_courses"),
    path("get_units/", note_views.get_units, name="get_units"),
    path("submit_notes/", note_views.submit_notes, name="submit_notes"),
    path("unit_details/<int:unit_id>/", note_views.unit_details, name="unit_details"),
    path(
        "course_details/<int:course_id>/",
        note_views.course_details,
        name="course_details",
    ),
    path("mpesa", views.mpesa, name="mpesa"),
    path("sitemap.xml", views.sitemap, name="sitemap"),
    path("robots.txt", views.robots, name="robots"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
