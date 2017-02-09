# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-31 11:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_merge_20170126_2111'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='allergies',
            field=models.CharField(blank=True, max_length=30, verbose_name='allergies'),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('male', 'male'), ('female', 'female'), ('other', 'other')], default=None, max_length=50),
            preserve_default=False,
        ),
    ]
