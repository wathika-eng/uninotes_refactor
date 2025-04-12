# Generated by Django 5.2 on 2025-04-12 19:50

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mainapp", "0002_alter_note_file_alter_note_status_alter_note_title"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name="note",
            index=models.Index(
                fields=["-uploaded_at"], name="mainapp_not_uploade_90ee07_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="unit",
            index=models.Index(
                fields=["course"], name="mainapp_uni_course__94f7ea_idx"
            ),
        ),
    ]
