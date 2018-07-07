# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection, connections
from articulos.views import dictfetchall

import csv
import codecs
import datetime
import os

# Import Models
from .models import Estacion, PuntoVentaDispositivo, Jornada, PlatcoCSV

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

class PlatcoCSVAddView(LoginRequiredMixin, View):
    """
    Subir archivo .CSV generado en la plataforma de platco
    """
    login_url = '/login/'
    def get(self, request):
        return render(request, "ventas/platco-csv-form.html", {})

    def post(self, request):
        fecha = datetime.datetime.strptime(request.POST.get("fecha"), "%d-%m-%Y").date()
        banco = request.POST.get("banco")

        ctx = {
            "mensaje": "El archivo .CSV ha sido subido correctamente!",
            "success": True,
            "action": "saving"
        }

        if request.POST and request.FILES:
            csvfile = request.FILES['archivo']
            reader = csv.reader(csvfile, delimiter=',')
            
            # Verificar si el archivo es del banco seleccionado
            try:  
                if not banco in list(reader)[0][0]:
                    # Si no corresponde mostramos mensaje de error y detenemos
                    ctx["mensaje"] = "El archivo no corresponde a la estructura del Banco %s" % banco
                    ctx["success"] = False
                    return render(request, "ventas/platco-csv-form.html", ctx)                    
            except:pass
        
        # Verificar si ya existe un registro del dia y el banco
        archivos = PlatcoCSV.objects.filter(fecha=fecha).filter(banco=banco)
        if archivos:
            archivos[0].archivo = request.FILES['archivo']
            archivos[0].save()
        else:
            archivo         = PlatcoCSV()
            archivo.archivo = request.FILES['archivo']
            archivo.fecha   = fecha
            archivo.banco   = banco
            archivo.save()

        return render(request, "ventas/platco-csv-form.html", ctx)

class JornadaVerifyView(LoginRequiredMixin, View):
    def get(self, request):
        estaciones   = Estacion.objects.all()
        ctx = {
            "estaciones":estaciones
        }
        return render(request, "ventas/jornada-form.html", ctx)

    def post(self, request):
        fecha        = request.POST.get("fecha")
        estacion     = request.POST.get("estacion")
        dispositivo  = request.POST.get("dispositivo")
        fecha_object = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()

        estacion = Estacion.objects.get(numero=estacion)

        ticket_malos = []
        ticket_no_csv = []

        # Obtener datos de la base de datos de leonux
        with connections['leonux'].cursor() as cursor:
            cursor.execute("SELECT id, auto_usuario, codigo_usuario, nombre_usuario, fecha_alta as fecha FROM pos_jornadas_sesion WHERE estacion = %s AND fecha_alta = %s", [estacion.serial, fecha])
            secciones = dictfetchall(cursor)

            for sesion in secciones:
                # Obtener datos del archivo CSV
                platco       = PlatcoCSV.objects.filter(fecha=fecha_object)
                if platco:
                    archivo  = open(platco[0].archivo.path)
                    reader   = csv.reader(archivo, delimiter=',')

                    sql = "SELECT auto_documento, fecha, hora, importe, codigo_banco, codigo_operacion FROM `pos_jornadas_detalle` WHERE id_sesion = %s AND tipo != 'ING' AND tipo != 'RET'" % sesion["id"]                    
                    cursor.execute(sql)
                    tickets = dictfetchall(cursor)

                    # Recorrer datos del csv
                    i = 0  
                    try:
                        for ticket in tickets:                            
                            for row in reader:
                                if i > 4 and row[0] != "Totales":
                                    if ticket["codigo_banco"] in row[5] and ticket["codigo_operacion"] in row[6]:
                                        # EXISTE EL TICKET VERIFICAMOS EL MONTO
                                        importe = float(ticket["importe"])
                                        importe2 = float(row[9])
                                       
                                        if not importe == importe2:
                                            ticket_malo = {                                                
                                                "leonux": {
                                                    "factura": ticket["auto_documento"],
                                                    "fecha": ticket["fecha"],
                                                    "hora": ticket["hora"],
                                                    "importe": ticket["importe"],
                                                    "codigo_banco": ticket["codigo_banco"],
                                                    "codigo_operacion": ticket["codigo_operacion"]
                                                },
                                                "platco": {
                                                    "terminal": row[0],
                                                    "lote": row[1],
                                                    "fecha": row[3],
                                                    "tarjeta": row[5],
                                                    "autorizacion": row[6],
                                                    "importe": row[9],
                                                }
                                            }
                                            ticket_malos.append(ticket_malo.copy())
                                    else:
                                        if i-4 == len(list(reader)):
                                            ticket_malo = {
                                                "factura": ticket["auto_documento"],
                                                "fecha": ticket["fecha"],
                                                "hora": ticket["hora"],
                                                "importe": ticket["importe"],
                                                "codigo_banco": ticket["codigo_banco"],
                                                "codigo_operacion": ticket["codigo_operacion"]
                                            }
                                            ticket_no_csv.append(ticket_malo.copy())

                                i = i + 1
                    except Exception as e: print e

        print ticket_malos