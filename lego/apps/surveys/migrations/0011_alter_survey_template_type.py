# Generated by Django 4.0.6 on 2022-08-22 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0010_alter_answer_created_by_alter_answer_updated_by_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="survey",
            name="template_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("company_presentation", "company_presentation"),
                    ("lunch_presentation", "lunch_presentation"),
                    ("alternative_presentation", "alternative_presentation"),
                    ("course", "course"),
                    ("breakfast_talk", "breakfast_talk"),
                    ("kid_event", "kid_event"),
                    ("party", "party"),
                    ("social", "social"),
                    ("other", "other"),
                    ("event", "event"),
                ],
                max_length=30,
                null=True,
                unique=True,
            ),
        ),
    ]
