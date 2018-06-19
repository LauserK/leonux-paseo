# -*- coding: utf-8 -*-
from django.views.generic import View
from django.http import JsonResponse
from django.db import connection, connections
from articulos.views import dictfetchall
import json, math
from decimal import Decimal

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


"""
POS IOS SERVICES
"""

class Groups(View):
    def post(self, request):
        section = request.GET.get('section')
        with connections['leonux'].cursor() as cursor:
            cursor.execute("SELECT auto FROM pos_secciones WHERE codigo = %s", [section])
            try:
                auto = dictfetchall(cursor)[0]["auto"]
                cursor.execute("SELECT pos_secciones_grupos.auto_grupo, productos_grupo.nombre FROM pos_secciones_grupos INNER JOIN productos_grupo ON productos_grupo.auto = pos_secciones_grupos.auto_grupo WHERE pos_secciones_grupos.auto_seccion = %s ORDER BY `productos_grupo`.`nombre` ASC", [auto])
                groups = dictfetchall(cursor)
            except:
                return APIResponse(None, "the section doesnt exists", None)

        return APIResponse(groups, "group list", True)

class Articles(View):
    def post(self, request):
        group = request.GET.get('group')
        article_code = request.GET.get('code')
        article_plu = request.GET.get('plu')

        with connections['leonux'].cursor() as cursor:
            # if is only one article by his code
            if article_code is not None:
                cursor.execute("SELECT auto, codigo, nombre, tasa, precio_pto AS precio_neto FROM `productos`WHERE estatus = 'Activo' AND codigo = %s", [article_code])
                
                try:
                    article = dictfetchall(cursor)[0]
                except:
                    return APIResponse(None, "The article not exists", False)    

                return APIResponse(article, "article", True)

            # if is only one article by his plu
            if article_plu is not None:
                cursor.execute("SELECT auto, codigo, nombre, tasa, precio_pto AS precio_neto FROM `productos`WHERE estatus = 'Activo' AND plu = %s", [article_plu])
                
                try:
                    article = dictfetchall(cursor)[0]
                except:
                    return APIResponse(None, "The article not exists", False)    

                return APIResponse(article, "article", True)

            # if is all articles of a group
            cursor.execute("SELECT auto, codigo, nombre, tasa, precio_pto AS precio_neto FROM `productos`WHERE estatus = 'Activo' AND auto_grupo = %s AND precio_pto != 0.00 ORDER BY nombre", [group])
            articles = dictfetchall(cursor)

        return APIResponse(articles, "article list", True)

class GetAllArticlesAccount(View):
    def post(self, request):
        code = request.GET.get('client')
        account = ""
        with connections['leonux'].cursor() as cursor:
            json_data = json.loads(request.body)
            try:
                client  = json_data["client"]
                account = str(client["code"][-5:]).zfill(5)
            except: pass

            if code:
                account = str(code[-5:]).zfill(5)

            cursor.execute("SELECT auto, auto_producto, nombre, codigo, cantidad, precio_item as precio_neto, tasa FROM pos_comandas WHERE cuenta = %s", [account])
            articles = dictfetchall(cursor)

        return APIResponse(articles, "article list", True)  

class AddArticleAccount(View):
    def post(self, request):
        json_data = json.loads(request.body)

        article_data   = json_data["article"]
        client    = json_data["client"]
        # Get the last 5 digits of the client code and add zeros until the string len be 5
        account    = str(client["code"][-5:]).zfill(5)
        auto_nuevo = ""

        with connections['leonux'].cursor() as cursor:
            cursor.execute("SELECT auto FROM pos_cuentas WHERE cuenta = %s", [account])
            accounts = dictfetchall(cursor)

            try:
                auto_nuevo = accounts[0]["auto"]
            except:pass

            if not len(accounts) > 0:
                """
                If the account doesnt exists create the new account with the last 4 digits of client code
                """
                cursor.execute("SELECT a_pos_cuentas FROM sistema_contadores limit 1")
                auto = int(dictfetchall(cursor)[0]["a_pos_cuentas"])
                auto_nuevo = str(auto + 1).zfill(10)

                cursor.execute("INSERT INTO `00000001`.`pos_cuentas` (`auto`, `cuenta`, `estatus_cuenta`, `estatus_servicio`, `estatus_abierta`, `estatus`, `acumulado`, `auto_cliente`, `ci_rif`, `nombre`, `dir_fiscal`, `hora`, `fin`, `corte`) VALUES (%s, %s, '0', '0', '0', 'Activo', '0.00', '', '', '', '', '', '', '0')", [auto_nuevo, account])

                cursor.execute("UPDATE `00000001`.`sistema_contadores` SET `a_pos_cuentas` = %s WHERE a_pos_cuentas != '' LIMIT 1", [auto_nuevo])    

            """
            Add the article to the account
            """
            cursor.execute("SELECT auto, nombre, codigo, auto_departamento, auto_grupo, auto_subgrupo, auto_tasa, precio_pto, tasa FROM productos WHERE codigo = %s", [article_data["code"]])
            
            try:
                article = dictfetchall(cursor)[0]
            except:
                return APIResponse(None, "article not exists", False)
            
            # Totals
            quantity = "%.3f" % float(article_data["quantity"])
            amount_global = Decimal("%.2f" % round(article["precio_pto"] * Decimal(quantity),2))
            tax = Decimal("%.2f" % round(Decimal(round((article["precio_pto"] * article["tasa"] / 100),2)) * Decimal(quantity),2))
            total = amount_global + tax


            cursor.execute("SELECT a_pos_comandas FROM sistema_contadores limit 1")
            auto = int(dictfetchall(cursor)[0]["a_pos_comandas"])
            auto_cuenta_row = str(auto + 1).zfill(10)

            cursor.execute("INSERT INTO pos_comandas (`auto`, `auto_producto`, `codigo`, `nombre`, `auto_departamento`, `auto_grupo`, `auto_subgrupo`, `auto_deposito`, `cantidad`, `empaque`, `precio_neto`, `descuento1p`, `descuento1`, `costo_venta`, `total_neto`, `tasa`, `impuesto`, `total`, `fecha`, `hora`, `deposito`, `precio_final`, `decimales`, `contenido_empaque`, `cantidad_und`, `precio_und`, `costo_und`, `precio_item`, `codigo_deposito`, `detalle`, `auto_tasa`, `categoria`, `costo_promedio_und`, `costo_compra`, `estatus_comanda`, `total_descuento`, `auto_vendedor`, `codigo_vendedor`, `auto_cuenta`, `cuenta`, `nombre_vendedor`, `detalle_cambio`) VALUES (%s, %s, %s, %s, %s, %s, %s, '0000000001', %s, 'UNIDAD', %s, '0.00', '0.00', '0.00', %s, %s, %s, %s, '2018-05-30', '20:00', 'PRINCIPAL',%s, '3', '0', '0.000', %s, '0.00', %s, '01', '', %s, '', '0.00', '0.00', '0', '0.00', '0000000001', '01', %s, %s, 'DIRECTO', '');", [auto_cuenta_row, article["auto"], article["codigo"], article["nombre"], article["auto_departamento"], article["auto_grupo"], article["auto_subgrupo"], quantity, article["precio_pto"], amount_global, article["tasa"], tax, total, article["precio_pto"], article["precio_pto"], article["precio_pto"], article["auto_tasa"], auto_nuevo, account])

            cursor.execute("UPDATE `00000001`.`sistema_contadores` SET `a_pos_comandas` = %s WHERE a_pos_comandas != '' LIMIT 1", [auto_cuenta_row])
            
            ctx = [{
                "auto": auto_cuenta_row
            }]
        return APIResponse(ctx, "saved", True)


class RemoveArticleAccount(View):
    def post(self, request):
        json_data    = json.loads(request.body)
        article_data = json_data["article"]

        with connections['leonux'].cursor() as cursor:
            cursor.execute("DELETE FROM pos_comandas WHERE auto = %s", [article_data["auto_row"]])

        return APIResponse(None, "removed", True)

class RemoveAllArticleAccount(View):
    def post(self, request):
        json_data    = json.loads(request.body)
        client    = json_data["client"]
        # Get the last 4 digits of the client code and add zeros until the string len be 5
        account    = str(client["code"][-5:]).zfill(5)

        with connections['leonux'].cursor() as cursor:
            cursor.execute("DELETE FROM pos_comandas WHERE cuenta = %s", [account])

        return APIResponse(None, "removed", True)


class GetClientByQueue(View):
    def post(self, request):
        section = request.GET.get('section')
        status  = request.GET.get('status') or '0'

        with connections['leonux'].cursor() as cursor:
            cursor.execute("SELECT id, pos_turno.rif, pos_turno.razon_social, pos_turno.ci as codigo, pos_turno.nombre, clientes.auto FROM `pos_turno` INNER JOIN clientes ON clientes.codigo = pos_turno.ci WHERE seccion = %s AND pos_turno.estatus = %s", [section, status])
            clients = dictfetchall(cursor)

        return APIResponse(clients, "client list", True)

class UpdateClientStatus(View):
    def post(self, request):
        client = request.GET.get('auto')
        status = request.GET.get('status')
        with connections['leonux'].cursor() as cursor:
            cursor.execute("UPDATE pos_turno SET estatus = %s WHERE id = %s", [status, client])
            return APIResponse(None, "updated", True)