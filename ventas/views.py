# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Import Models
from .models import Estacion, PuntoVentaDispositivo, Jornada

class HomeView(LoginRequiredMixin,TemplateView):
    """
    muestra todas las opciones de cierre
    """
    template_name = "menus/cierres.html"

class EstacionesView(View):
    """
    Muestra una lista de las estaciones
    """
    login_url = '/login/'
    def get(self, request):

        estaciones = Estacion.objects.all()

        ctx = {
            "estaciones": estaciones
        }

        return render(request, "ventas/estacion-list.html", ctx)

class EstacionesEditView(LoginRequiredMixin, View):
    """
    Muestra un formulario para editar la estacion
    """
    login_url = '/login/'

    def get(self, request, estacion_id):
        estacion = get_object_or_404(Estacion, numero=estacion_id)

        ctx = {
            "estacion": estacion,
            "action": "edit"
        }

        return render(request, "ventas/estacion-form.html", ctx)

    def post(self, request, estacion_id):
        numero = request.POST.get("numero_estacion")
        serial = request.POST.get("serial_estacion")

        estacion = get_object_or_404(Estacion, numero=estacion_id)
        estacion.numero = numero
        estacion.serial = serial
        
        ctx = {
            "mensaje": "El modelo ha sido modificado correctamente!",
            "success": True,
            "action": "saving"
        }

        try:
            estacion.save()
        except:
            ctx["mensaje"] = "¡Ha ocurrido un error al intentar guardar la información!"
            ctx["success"] = False
        
        return render(request, "ventas/estacion-form.html", ctx)


class EstacionesAddView(LoginRequiredMixin, View):
    """
    Muestra formulario para agregar una nueva estacion
    """
    login_url = '/login/'

    def get(self, request):
        return render(request, "ventas/estacion-form.html", {"action":"create"})

    def post(self, request):
        numero = request.POST.get("numero_estacion")
        serial = request.POST.get("serial_estacion")

        estacion = Estacion()
        estacion.numero = numero
        estacion.serial = serial
        
        ctx = {
            "mensaje": "La estación ha sido registrada correctamente!",
            "success": True,
            "action": "saving"
        }

        try:
            estacion.save()
        except:
            ctx["mensaje"] = "¡Ha ocurrido un error al intentar guardar la información!"
            ctx["success"] = False
        
        return render(request, "ventas/estacion-form.html", ctx)

class EstacionesDestroyView(LoginRequiredMixin, View):
    """
    Muestra pregunta para eliminar una estación
    """
    login_url = '/login/'

    def get(self, request, estacion_id):
        estacion = get_object_or_404(Estacion, numero=estacion_id)

        ctx = {
            "mensaje": "¿Estás seguro de eliminar la estación: %s?" % estacion.numero,
            "success": False,
            "action": "destroy"
        }
        return render(request, "ventas/estacion-form.html", ctx)

    def post(self, request, estacion_id):
        estacion = get_object_or_404(Estacion, numero=estacion_id)
        estacion.delete()
        
        ctx = {
            "mensaje": "La estación ha sido eliminada correctamente!",
            "success": True,
            "action": "saving"
        }

        return render(request, "ventas/estacion-form.html", ctx)

class DispositivoView(View):
    """
    Muestra una lista de los punto de ventas
    """
    login_url = '/login/'
    def get(self, request):

        dispositivos = PuntoVentaDispositivo.objects.all()
        estaciones   = Estacion.objects.all()

        ctx = {
            "dispositivos": dispositivos,
            "estaciones": estaciones
        }

        return render(request, "ventas/dispositivo-list.html", ctx)

class DispositivoEditView(LoginRequiredMixin, View):
    """
    Muestra un formulario para editar un punto de venta
    """
    login_url = '/login/'

    def get(self, request, dispositivo_id):
        dispositivo = get_object_or_404(PuntoVentaDispositivo, numero=dispositivo_id)
        estaciones   = Estacion.objects.all()

        ctx = {
            "dispositivo": dispositivo,
            "estaciones": estaciones,
            "action": "edit"
        }

        return render(request, "ventas/dispositivo-form.html", ctx)

    def post(self, request, dispositivo_id):
        numero   = request.POST.get("numero_dispositivo")
        serial   = request.POST.get("serial_dispositivo")
        estacion = request.POST.get("numero_estacion")

        dispositivo = get_object_or_404(PuntoVentaDispositivo, numero=dispositivo_id)
        dispositivo.numero = numero
        dispositivo.serial = serial

        # get the station
        estacion = Estacion.objects.get(numero=estacion)
        
        dispositivo.estacion = estacion


        ctx = {
            "mensaje": "El modelo ha sido modificado correctamente!",
            "success": True,
            "action": "saving"
        }

        try:
            dispositivo.save()
        except:
            ctx["mensaje"] = "¡Ha ocurrido un error al intentar guardar la información!"
            ctx["success"] = False
        
        return render(request, "ventas/dispositivo-form.html", ctx)


class DispositivoAddView(LoginRequiredMixin, View):
    """
    Muestra formulario para agregar un nuevo punto de venta
    """
    login_url = '/login/'

    def get(self, request):
        estaciones = Estacion.objects.all()

        ctx = {
            "action":"create",
            "estaciones":estaciones
        }
        return render(request, "ventas/dispositivo-form.html", ctx)

    def post(self, request):
        numero   = request.POST.get("numero_dispositivo")
        serial   = request.POST.get("serial_dispositivo")
        estacion = request.POST.get("numero_estacion")

        dispositivo        = PuntoVentaDispositivo()
        dispositivo.numero = numero
        dispositivo.serial = serial

        # get the station
        estacion = Estacion.objects.get(numero=estacion)
        
        dispositivo.estacion = estacion
        
        ctx = {
            "mensaje": "La estación ha sido registrada correctamente!",
            "success": True,
            "action": "saving"
        }

        try:
            dispositivo.save()
        except:
            ctx["mensaje"] = "¡Ha ocurrido un error al intentar guardar la información!"
            ctx["success"] = False
        
        return render(request, "ventas/dispositivo-form.html", ctx)

class DispositivoDestroyView(LoginRequiredMixin, View):
    """
    Muestra pregunta para eliminar un punto de venta
    """
    login_url = '/login/'

    def get(self, request, dispositivo_id):
        dispositivo = get_object_or_404(PuntoVentaDispositivo, numero=dispositivo_id)

        ctx = {
            "mensaje": "¿Estás seguro de eliminar el punto de venta: %s?" % dispositivo.numero,
            "success": False,
            "action": "destroy"
        }
        return render(request, "ventas/dispositivo-form.html", ctx)

    def post(self, request, dispositivo_id):
        dispositivo = get_object_or_404(PuntoVentaDispositivo, numero=dispositivo_id)
        dispositivo.delete()
        
        ctx = {
            "mensaje": "El punto de venta ha sido eliminada correctamente!",
            "success": True,
            "action": "saving"
        }

        return render(request, "ventas/dispositivo-form.html", ctx)



class PlatcoCSV(View):
    def post(self, request):
        pass