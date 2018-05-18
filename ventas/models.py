from __future__ import unicode_literals
from usuarios.models import User
from django.db import models

class Estacion(models.Model):
    numero = models.IntegerField(default=0, unique=True)
    serial = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Estaciones"
    
    def __unicode__(self):
        return "%s - %s" % (self.numero, self.serial)


class PuntoVentaDispositivo(models.Model):
    numero   = models.IntegerField(default=1, unique=True)
    serial   = models.CharField(max_length=100, unique=True)
    estacion = models.ForeignKey(Estacion)

    class Meta:
        verbose_name = "Dispositivos Punto de Venta"

    def __unicode__(self):
        return "%s - %s | Estacion: %s" % (self.numero, self.serial, self.estacion.numero)

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
    dia         = models.DateField(auto_now_add=True, blank=True)
    diferencia  = models.DecimalField(max_digits=20, decimal_places=2)