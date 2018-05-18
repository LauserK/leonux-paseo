from django.contrib import admin
from .models import Estacion, PuntoVentaDispositivo, Jornada


@admin.register(Estacion)
class EstacionAdmin(admin.ModelAdmin):
    pass

@admin.register(PuntoVentaDispositivo)
class PuntoVentaDispositivoAdmin(admin.ModelAdmin):
    pass

@admin.register(Jornada)
class JornadaAdmin(admin.ModelAdmin):
    pass