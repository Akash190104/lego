# Generated by Django 2.2.13 on 2021-03-09 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0030_auto_20210207_1637"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="legacy_registration_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
