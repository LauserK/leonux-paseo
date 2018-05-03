from django.db import models
from django.contrib.auth.models import AbstractUser
from articulos.models import Reporte

class TipoUsuario(models.Model):
    codigo   = models.CharField(max_length=12)
    nombre   = models.CharField(max_length=50)
    reportes = models.ManyToManyField(Reporte, blank=True)

class User(AbstractUser):
    tipo_usuario = models.ForeignKey(TipoUsuario, blank=True, null=True)
