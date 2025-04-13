# main/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Course, Unit, Note


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "daily"

    def items(self):
        return ["dashboard"]  # your static view names

    def location(self, item):
        return reverse(item)


class CourseSitemap(Sitemap):
    def items(self):
        return Course.objects.all().order_by("id")


class UnitSitemap(Sitemap):
    def items(self):
        return Unit.objects.all().order_by("id")


class NoteSitemap(Sitemap):
    def items(self):
        return Note.objects.all().order_by("-uploaded_at")  # Most recent first
