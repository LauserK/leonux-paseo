from __future__ import unicode_literals
from django.db import models

class Reporte(models.Model):
    nombre = models.CharField(blank=True, max_length=100)
    url    = models.CharField(blank=True, max_length=100, unique=True)
    icono  = models.CharField(default="chrome_reader_mode", max_length=100)
    
    def __unicode__(self):
        return self.nombre

    def get_url(self):
        return "/reportes/%s" % self.url
