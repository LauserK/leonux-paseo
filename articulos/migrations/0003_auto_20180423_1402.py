# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-23 18:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articulos', '0002_auto_20180422_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reporte',
            name='url',
            field=models.CharField(blank=True, max_length=100, unique=True),
        ),
    ]