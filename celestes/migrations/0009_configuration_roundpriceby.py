# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-03-06 15:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('celestes', '0008_auto_20200305_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='roundPriceBy',
            field=models.DecimalField(decimal_places=2, default=500.0, max_digits=11),
        ),
    ]
