# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-05-03 14:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Estacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField(default=0)),
                ('serial', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Jornada',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_lote', models.CharField(max_length=30)),
                ('total_tdd', models.DecimalField(decimal_places=2, max_digits=20)),
                ('total_tdc', models.DecimalField(decimal_places=2, max_digits=20)),
                ('total_ces', models.DecimalField(decimal_places=2, max_digits=20)),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('cajero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jornada_usuario_cajero', to=settings.AUTH_USER_MODEL)),
                ('estacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.Estacion')),
            ],
        ),
        migrations.CreateModel(
            name='PuntoVentaDispositivo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField(default=1)),
                ('serial', models.CharField(max_length=100)),
                ('estacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.Estacion')),
            ],
        ),
        migrations.AddField(
            model_name='jornada',
            name='punto_venta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.PuntoVentaDispositivo'),
        ),
        migrations.AddField(
            model_name='jornada',
            name='supervisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jornada_usuario_supervisor', to=settings.AUTH_USER_MODEL),
        ),
    ]