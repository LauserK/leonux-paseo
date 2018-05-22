from __future__ import unicode_literals
from usuarios.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import datetime

def csv_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'csv-platco/{0}_{1}.csv'.format(instance.banco, instance.fecha)

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


class PlatcoCSV(models.Model):
    fecha   = models.DateField(default=datetime.date.today, auto_now=False, auto_now_add=False)
    bancos  = (
        ('Mercantil', 'Banco Mercantil'),
        ('Provincial', 'Banco Provincial'),
	)
    banco   = models.CharField(max_length=50, choices=bancos, default="mercantil")
    archivo = models.FileField(upload_to=csv_directory_path, blank=True, default="")

    class Meta:
        verbose_name_plural = "Archivos CSV Platco"

    def __unicode__(self):
        return "%s | %s" % (self.banco, self.fecha)

    def save(self, *args, **kwargs):
        try:
            this = PlatcoCSV.objects.get(id=self.id)
            if this.archivo != self.archivo:
                this.archivo.delete()
        except: pass
        super(PlatcoCSV, self).save(*args, **kwargs)

@receiver(pre_delete, sender=PlatcoCSV)
def PlatcoCSV_delete(sender, instance, **kwargs):
    """
    Elimina el archivo .csv asociado al modelo a eliminar
    """
    try:
        instance.archivo.delete(False)
    except: pass