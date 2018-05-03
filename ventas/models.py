from __future__ import unicode_literals
from usuarios.models import User
from django.db import models

class Estacion(models.Model):
    numero = models.IntegerField(default=0)
    serial = models.CharField(max_length=100)

class PuntoVentaDispositivo(models.Model):
    numero   = models.IntegerField(default=1)
    serial   = models.CharField(max_length=100)
    estacion = models.ForeignKey(Estacion)

class Jornada(models.Model):
    estacion    = models.ForeignKey(Estacion)
    numero_lote = models.CharField(max_length=30)
    punto_venta = models.ForeignKey(PuntoVentaDispositivo)
    total_tdd   = models.DecimalField(max_digits=20, decimal_places=2)
    total_tdc   = models.DecimalField(max_digits=20, decimal_places=2)
    total_ces   = models.DecimalField(max_digits=20, decimal_places=2)
    total       = models.DecimalField(max_digits=20, decimal_places=2)
    supervisor  = models.ForeignKey(User, related_name='jornada_usuario_supervisor')
    cajero      = models.ForeignKey(User, related_name='jornada_usuario_cajero')