# -*- coding: utf-8 -*-
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection, connections
from articulos.views import dictfetchall
import json

# Import Models
from .models import Estacion, PuntoVentaDispositivo, Jornada

def APIResponse(data, message, success):
	settings = {
		"success": success,
		"message": message
	}
	if data is not None:
		return JsonResponse({"data": data, "settings":settings})
	else:
		return JsonResponse({"data": [], "settings": settings})

class Stations(View):
    def get(self,request):
        """
        Returns a list of all stations on DB

        Returns
        -------
        {"data": [serial, id, numero], ...}
        """
        stations = list(Estacion.objects.all().values())
        return APIResponse(stations, "Stations list", True)

class Devices(View):
    def get(self, request, station_id):
        """
        Returns a list of all devices associate to station on DB

        Returns
        -------
        {"data": [serial, id, numero, estacion_id], ...}
        """
        station = Estacion.objects.get(numero=station_id)
        devices = list(PuntoVentaDispositivo.objects.filter(estacion=station).values())
        return APIResponse(devices, "Devices list", True)

class Sessions(View):
    def get(self, request, station_id):
        station = Estacion.objects.get(numero=station_id)
        with connections['leonux'].cursor() as cursor:
            # Get the session open on the selected station
            cursor.execute("SELECT id, auto_usuario, codigo_usuario, nombre_usuario, fecha_alta as fecha FROM pos_jornadas_sesion WHERE estacion = %s AND estatus_cierre = 0", [station.serial])

            try:
                """
                Verify if exists the session
                """
                sessions = dictfetchall(cursor)[0]
            except:
                return APIResponse(None, "The session requested not exists", False)
            
            # Search the data of the open session
            cursor.execute("SELECT id_sesion, tdb, tcr, sod, ces FROM pos_jornadas_sesion_arqueo WHERE id_sesion = %s", [sessions["id"]])
            session = dictfetchall(cursor)
            
            # Search all NDC (Notas de Credito)            
            sql = "SELECT SUM(total) as total_ndc FROM ventas WHERE tipo = 03 AND auto_usuario = %s AND fecha = '%s' and estacion = '%s' GROUP by tipo" % (sessions["auto_usuario"], sessions["fecha"], station.serial)
            cursor.execute(sql)
            try:
                ndc = dictfetchall(cursor)[0]["total_ndc"]
            except:
                ndc = "0.00"

            data = [{
                "id": session[0]["id_sesion"],
                "codigo_usuario": sessions["codigo_usuario"],
                "nombre_usuario": sessions["nombre_usuario"],
                "notas_creditos": ndc or "0.00",
                "sod": session[0]["sod"] or "0.00",
                "ces": session[0]["ces"] or "0.00",
                "tdc": session[0]["tcr"] or "0.00",
                "tdd": session[0]["tdb"] or "0.00",
            }]

            return APIResponse(data, "Active session", True)


class Tickets(View):
    def get(self, request, station_id, ticket_number):
        """
        Returns data from a specific ticket getting by the operation number
        """
        try:
            station = Estacion.objects.get(numero=station_id)
        except:
            return APIResponse(None, "The station requested not exists", False)

        with connections['leonux'].cursor() as cursor:
            # Get the session open on the selected station
            cursor.execute("SELECT id, auto_usuario, codigo_usuario, nombre_usuario, fecha_alta as fecha FROM pos_jornadas_sesion WHERE estacion = %s AND estatus_cierre = 0", [station.serial])

            try:
                """
                Verify if exists the session
                """
                sessions = dictfetchall(cursor)[0]
            except:
                return APIResponse(None, "The session requested not exists", False)

            # Get the ticket data from database
            cursor.execute("SELECT tipo, codigo_banco, codigo_operacion, hora, fecha, importe, auto_documento AS factura FROM pos_jornadas_detalle WHERE id_sesion = %s AND codigo_operacion = %s", [sessions["id"], ticket_number])

            try:
                """
                Verify if exists the ticket
                """
                ticket = dictfetchall(cursor)[0]
                # Get the bill number
                cursor.execute("SELECT documento FROM ventas WHERE auto = %s", [ticket["factura"]])
                ticket["factura"] = dictfetchall(cursor)[0]["documento"]

            except:
                return APIResponse(None, "The ticket requested not exists", False)

        return APIResponse(ticket, "Ticket %s" % ticket_number, True)

class Report(View):
    def post(self, request, station_id):
        json_data = json.loads(request.body)

        estacion_numero = json_data["estacion_numero"]
        loten_numero = json_data["lote_numero"]
        pv_numero = json_data["pv_numero"]
        total_tdd = json_data["total_tdd"]
        total_tdc = json_data["total_tdc"]

        tickets_json = json_data["tickets"]
        tickets = []
        
        for ticket in tickets_json:
            pass

        return APIResponse(None, "The report was saved", True)