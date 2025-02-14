# Generated by Django 4.0.6 on 2022-08-30 20:39

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0035_alter_user_student_username"),
    ]

    operations = [
        migrations.CreateModel(
            name="PhotoConsent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now, editable=False
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                (
                    "deleted",
                    models.BooleanField(db_index=True, default=False, editable=False),
                ),
                (
                    "semester",
                    models.CharField(
                        choices=[("spring", "spring"), ("autumn", "autumn")],
                        max_length=6,
                    ),
                ),
                ("year", models.PositiveIntegerField()),
                (
                    "domain",
                    models.CharField(
                        choices=[
                            ("WEBSITE", "WEBSITE"),
                            ("SOCIAL_MEDIA", "SOCIAL_MEDIA"),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "is_consenting",
                    models.BooleanField(blank=True, default=None, null=True),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        default=None,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        default=None,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="photo_consents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
                "default_manager_name": "objects",
            },
        ),
    ]
