# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-03-23 11:38
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('celestes', '0012_article_isforsell'),
    ]

    operations = [
        migrations.AddField(
            model_name='movementarticle',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime.now),
        ),
    ]