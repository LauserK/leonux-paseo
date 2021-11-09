# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-03-05 14:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('celestes', '0004_auto_20200305_1043'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='ingredients',
            field=models.ManyToManyField(blank=True, null=True, related_name='_article_ingredients_+', to='celestes.Article'),
        ),
        migrations.AddField(
            model_name='article',
            name='quantity',
            field=models.DecimalField(decimal_places=3, default=1, max_digits=12),
        ),
    ]
