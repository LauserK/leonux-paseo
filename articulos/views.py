# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from usuarios.models import User
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponse
from django.db import connection, connections
from datetime import datetime, timedelta
from .models import Reporte
from ventas.models import Estacion
from django.http import Http404
import json


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class ReporteCompanyView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):
        ctx = {}
        template   = "menus/company.html"
        return render(request, template, ctx)

class ReporteMenuView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request, company_id):
        reportes = request.user.tipo_usuario.reportes.all()
        ctx = {
            "company_id": company_id,
            "reportes":reportes
        }
        template   = "menus/reportes.html"
        return render(request, template, ctx)

class ArticuloReporteView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request, company_id):
        if not request.user.tipo_usuario.reportes.filter(url="articulos").exists():
            raise Http404("NO TIENES PERMISOS PARA VISUALIZAR ESTA PÁGINA")

        cursor = connections['leonux'].cursor()        
        if company_id == '2':            
            cursor = connections['celestes'].cursor()
        with cursor:
            # Obtener los proveedores
            cursor.execute("SELECT auto, razon_social, ci_rif FROM proveedores WHERE estatus = 'Activo' ORDER BY razon_social")
            proveedores = dictfetchall(cursor)

            # Obtener los departamentos del sistema
            cursor.execute("SELECT auto, nombre FROM empresa_departamentos ORDER BY nombre")
            departamentos = dictfetchall(cursor)

            # Obtener los grupos/familias de los articulos
            cursor.execute("SELECT auto, nombre FROM productos_grupo ORDER BY nombre")
            grupos = dictfetchall(cursor)

            # Obtener las marcas de los articulos
            cursor.execute("SELECT auto, nombre FROM productos_marca ORDER BY nombre")
            marcas = dictfetchall(cursor)

            cursor.close()

            # Lista de categorias en el sistema
            categorias = [{"nombre": "Bien de Servicio"},{"nombre": "Materia Prima"},{"nombre": "Producto Terminado"},{"nombre": "Uso Interno"},{"nombre": "Producto Manufacturado"}]

        ctx        = {
            "company_id": company_id,
            "proveedores": proveedores,
            "departamentos": departamentos,
            "grupos": grupos,
            "subgrupos": "",
            "marcas": marcas,
            "categorias": categorias

        }
        template   = "reportes/articulo-index.html"
        return render(request, template, ctx)

    def post(self, request, company_id):
        # Obtenemos los filtros del formulario
        auto_proveedor    = request.POST.get("filtro-proveedor")
        referencia        = request.POST.get("filtro-referencia")
        auto_departamento = request.POST.get("filtro-departamento")
        auto_grupo        = request.POST.get("filtro-grupos")
        auto_marca        = request.POST.get("filtro-marcas")
        categoria         = request.POST.get("filtro-categorias")
        tipo_reporte      = request.POST.get("tipo-reporte")
        tipo_orden        = request.POST.get("orden") # WIP

        cursor = connections['leonux'].cursor()        
        if company_id == '2':            
            cursor = connections['celestes'].cursor()
        with cursor:
            # Filtros
            filtros = ""

            # Query sin filtros
            sql = "SELECT ventas_detalle.auto_producto AS auto, productos.codigo, productos.nombre FROM ventas_detalle INNER JOIN productos ON ventas_detalle.auto_producto = productos.auto WHERE productos.estatus = 'Activo'"

            # Obtener los articulos del proveedor mediante el filtro
            proveedor = {}
            if auto_proveedor is not None and auto_proveedor != "":
                cursor.execute("SELECT auto, razon_social, ci_rif FROM proveedores WHERE auto = %s", [auto_proveedor])
                proveedor = dictfetchall(cursor)[0]
                sql = "SELECT compras_detalle.auto_producto AS auto, compras_detalle.codigo, compras_detalle.nombre, productos.estatus FROM compras_detalle INNER JOIN compras ON compras.auto = compras_detalle.auto_documento INNER JOIN productos ON compras_detalle.auto_producto = productos.auto WHERE compras.auto_proveedor = %s and productos.estatus = 'Activo'" % auto_proveedor

            # Filtro por referencia (SI ES MARCADO O NO / 0|1)
            if referencia is not None and referencia != "":
                filtros = "%s AND productos.referencia = %s" % (filtros, referencia)

            # Obtener info del filtro (departamento)
            departamento = ""
            if auto_departamento is not None and auto_departamento != "":
                cursor.execute("SELECT auto, nombre FROM empresa_departamentos WHERE auto = %s", [auto_departamento])
                departamento = dictfetchall(cursor)[0]

                filtros = "%s AND productos.auto_departamento = %s" % (filtros, auto_departamento)

            # Obtener info del filtro (grupo)
            grupo = ""
            if auto_grupo is not None and auto_grupo != "":
                # Obtener e grupos/familias del filtro
                cursor.execute("SELECT auto, nombre FROM productos_grupo WHERE auto = %s", [auto_grupo])
                grupo = dictfetchall(cursor)[0]

                filtros = "%s AND productos.auto_grupo = %s" % (filtros, auto_grupo)

            marca = ""
            if auto_marca is not None and auto_marca != "":
            # Obtener la marcas del filtro
                cursor.execute("SELECT auto, nombre FROM productos_marca WHERE auto = %s", [auto_marca])
                marca = dictfetchall(cursor)[0]

                filtros = "%s AND productos.auto_marca = %s" % (filtros, auto_marca)

            if categoria is not None and categoria != "":
                filtros = "%s AND productos.categoria = '%s'" % (filtros, categoria)


            # Obtener los articulos
            sql_completo = sql + filtros + " GROUP BY auto"
            cursor.execute(sql_completo)
            articulos = dictfetchall(cursor)

            # Filtro de fechas para ventas
            filtro_ventas = request.POST.get("filtro-dias") # dias || fechas
            dias = 0
            desde = ""
            hasta = str(datetime.today().date()) # Por default hasta el dia de hoy

            # si es por dias (Hoy, dia anterior, ultimos 15 dias, etc)
            if filtro_ventas == "dias":
                dias = request.POST.get("filtro-dia")
                d = datetime.today() - timedelta(days=int(dias)) # Desde hoy descuenta los dias indicados
                desde = str(d.date()) # Lo pasamos a string
                if dias == "1": # Si la opcion es "Dia Anterior" solo mostramos los datos de ese dia especfico
                    hasta = desde
            elif filtro_ventas == "fechas": # Si es por rango de fechas
                desde = request.POST.get("filtro-desde")
                if request.POST.get("filtro-hasta") != "" and request.POST.get("filtro-hasta") is not None: # SI no se pasa una fecha es hasta hoy
                    hasta = request.POST.get("filtro-hasta")

            total = 0.00
            # Damos formato a los datos
            articulos_array = []
            for articulo in articulos:
                articulo_objeto = {
                    "codigo": articulo["codigo"],
                    "nombre": articulo["nombre"],
                    "depositos": [],
                    "cantidad_vendida": 0,
                    "cantidad_depositos": 0.00,
                    "monto_vendido":0.00
                }

                # Obtenemos los depositos
                cursor.execute("SELECT empresa_depositos.nombre, productos_deposito.fisica FROM productos_deposito INNER JOIN empresa_depositos ON productos_deposito.auto_deposito = empresa_depositos.auto WHERE productos_deposito.auto_producto = %s", [articulo["auto"]])
                # Ingresamos los datos al objeto del articulo
                depositos = dictfetchall(cursor)
                for deposito in depositos:
                    articulo_objeto["depositos"].append(deposito)
                    articulo_objeto["cantidad_depositos"] = float(articulo_objeto["cantidad_depositos"]) + float(deposito["fisica"])                

                cursor.execute("SELECT SUM(cantidad) as cantidad, SUM(total) AS total FROM ventas_detalle WHERE auto_producto = %s AND fecha >= %s AND fecha <= %s GROUP BY auto_producto", [articulo["auto"], desde, hasta])
                try:
                    cantidad = dictfetchall(cursor)[0]
                    articulo_objeto["cantidad_vendida"] = int(cantidad["cantidad"])
                    articulo_objeto["monto_vendido"] = float(cantidad["total"])
                    total += float(cantidad["total"])
                except:
                    pass

                # Agregamos el articulo a la lista
                articulos_array.append(articulo_objeto)

            # Cerramos la conexion
            cursor.close()


        ctx        = {
            "company_id": company_id,
            "articulos": articulos_array,
            "proveedor": proveedor,
            "referencia": referencia,
            "departamento": departamento,
            "grupo": grupo,
            "marca": marca,
            "categoria": categoria,
            "fecha": str(datetime.today().date().strftime('%d-%m-%Y')),
            "desde":desde,
            "hasta":hasta,
            "total": total
        }

        if tipo_reporte == "lista":
            template   = "reportes/reporte_articulo_lista.html"
            return render(request, template, ctx)
        elif tipo_reporte == "grafica-total":
            template   = "reportes/reporte_articulo_grafico_total.html"
            return render(request, template, ctx)

       # pdf = render_to_pdf(template, ctx)
        #return HttpResponse(pdf, content_type='application/pdf')

class VentasReporteView(View):
    def get(self, request, company_id):
        if not request.user.tipo_usuario.reportes.filter(url="ventas").exists():
            raise Http404("NO TIENES PERMISOS PARA VISUALIZAR ESTA PÁGINA")

        ctx = {}
        template = "reportes/ventas/ventas-index.html"
        return render(request, template, ctx)

    def post(self, request):
        if not request.user.tipo_usuario.reportes.filter(url="ventas").exists():
            raise Http404("NO TIENES PERMISOS PARA VISUALIZAR ESTA PÁGINA")

        cursor = connections['leonux'].cursor()        
        if company_id == '2':            
            cursor = connections['celestes'].cursor()
        with cursor:
            # Query sin filtros
            sql = "SELECT SUM(total) AS total, estacion FROM ventas WHERE documento_nombre = 'VENTA' "
            filtros = ""

            # Filtro de fechas para ventas
            filtro_ventas = request.POST.get("filtro-dias") # dias || fechas
            dias = 0
            desde = ""
            hasta = str(datetime.today().date()) # Por default hasta el dia de hoy

            # si es por dias (Hoy, dia anterior, ultimos 15 dias, etc)
            if filtro_ventas == "dias":
                dias = request.POST.get("filtro-dia")
                d = datetime.today() - timedelta(days=int(dias)) # Desde hoy descuenta los dias indicados
                desde = str(d.date()) # Lo pasamos a string
                if dias == "1": # Si la opcion es "Dia Anterior" solo mostramos los datos de ese dia especfico
                    hasta = desde

            elif filtro_ventas == "fechas": # Si es por rango de fechas
                desde = request.POST.get("filtro-desde")
                if request.POST.get("filtro-hasta") != "" and request.POST.get("filtro-hasta") is not None: # SI no se pasa una fecha es hasta hoy
                    hasta = request.POST.get("filtro-hasta")

            filtros = "AND fecha >= '%s' AND fecha <= '%s' " % (desde, hasta)
            sql_completo = sql + filtros + " GROUP BY estacion ORDER by serie"        
            cursor.execute(sql_completo)
            ventas = dictfetchall(cursor)
            
            # Totales
            total_venta = 0
            total_creditos = 0
            for venta in ventas:
                cursor.execute("SELECT usuario, SUM(total) as total FROM ventas WHERE documento_nombre = 'VENTA' AND estacion = %s AND fecha >= %s AND fecha <= %s GROUP BY usuario", [venta["estacion"], desde, hasta])
                usuarios = dictfetchall(cursor)

                cursor.execute("SELECT usuario, SUM(total) as total FROM ventas WHERE signo = '-1' AND estacion = %s AND fecha >= %s AND fecha <= %s GROUP BY usuario", [venta["estacion"], desde, hasta])
                creditos = dictfetchall(cursor)

                try:
                    venta["caja"]     = Estacion.objects.get(serial=venta["estacion"]).numero
                    venta["usuarios"] = usuarios
                    venta["creditos"] = creditos
                except:pass
                
                total_venta = total_venta + venta["total"]

                for credito in creditos:                    
                    total_creditos = total_creditos + credito["total"]

            cursor.close()
            totales = {
                "ventas": total_venta,
                "creditos": total_creditos,
                "total": total_venta - total_creditos

            }

        ctx = {
            "company_id": company_id,
            "ventas":ventas,
            "desde":desde,
            "fecha": str(datetime.today().date().strftime('%d-%m-%Y')),
            "hasta":hasta,
            "totales": totales
        }
        #template = "reportes/ventas/ventas-reporte-grafica.html"
        template = "reportes/ventas/ventas-reporte-lista.html"
        return render(request, template, ctx)

class VentaUsuarioReporteView(View):
    def get(self, request, company_id):
        if not request.user.tipo_usuario.reportes.filter(url="articulos").exists():
            raise Http404("NO TIENES PERMISOS PARA VISUALIZAR ESTA PÁGINA")

        cursor = connections['leonux'].cursor()        
        if company_id == '2':            
            cursor = connections['celestes'].cursor()
        with cursor:
            # Obtener los proveedores
            cursor.execute("SELECT auto, razon_social, ci_rif FROM proveedores WHERE estatus = 'Activo' ORDER BY razon_social")
            proveedores = dictfetchall(cursor)

            # Obtener los departamentos del sistema
            cursor.execute("SELECT auto, nombre FROM empresa_departamentos ORDER BY nombre")
            departamentos = dictfetchall(cursor)

            # Obtener los grupos/familias de los articulos
            cursor.execute("SELECT auto, nombre FROM productos_grupo ORDER BY nombre")
            grupos = dictfetchall(cursor)

            # Obtener las marcas de los articulos
            cursor.execute("SELECT auto, nombre FROM productos_marca ORDER BY nombre")
            marcas = dictfetchall(cursor)

            cursor.close()

            # Lista de categorias en el sistema
            categorias = [{"nombre": "Bien de Servicio"},{"nombre": "Materia Prima"},{"nombre": "Producto Terminado"},{"nombre": "Uso Interno"},{"nombre": "Producto Manufacturado"}]

        ctx = {
            "company_id": company_id,
            "proveedores": proveedores,
            "departamentos": departamentos,
            "grupos": grupos,
            "subgrupos": "",
            "marcas": marcas,
            "categorias": categorias
        }
        template = "reportes/ventas/ventasUsuario-index.html"
        return render(request, template, ctx)

    def post(self, request, company_id):
        # Obtenemos los filtros del formulario
        auto_proveedor    = request.POST.get("filtro-proveedor")
        referencia        = request.POST.get("filtro-referencia")
        auto_departamento = request.POST.get("filtro-departamento")
        auto_grupo        = request.POST.get("filtro-grupos")
        auto_marca        = request.POST.get("filtro-marcas")
        categoria         = request.POST.get("filtro-categorias")
        tipo_reporte      = request.POST.get("tipo-reporte")
        tipo_orden        = request.POST.get("orden") # WIP

        cursor = connections['leonux'].cursor()        
        if company_id == '2':            
            cursor = connections['celestes'].cursor()
        with cursor:
            # Filtros
            filtros = ""

            # Query sin filtros
            sql = "SELECT ventas_detalle.auto_producto AS auto, productos.codigo, productos.nombre FROM ventas_detalle INNER JOIN productos ON ventas_detalle.auto_producto = productos.auto WHERE productos.estatus = 'Activo'"

            # Obtener los articulos del proveedor mediante el filtro
            proveedor = {}
            if auto_proveedor is not None and auto_proveedor != "":
                cursor.execute("SELECT auto, razon_social, ci_rif FROM proveedores WHERE auto = %s", [auto_proveedor])
                proveedor = dictfetchall(cursor)[0]
                sql = "SELECT compras_detalle.auto_producto AS auto, compras_detalle.codigo, compras_detalle.nombre, productos.estatus FROM compras_detalle INNER JOIN compras ON compras.auto = compras_detalle.auto_documento INNER JOIN productos ON compras_detalle.auto_producto = productos.auto WHERE compras.auto_proveedor = %s and productos.estatus = 'Activo'" % auto_proveedor

            # Filtro por referencia (SI ES MARCADO O NO / 0|1)
            if referencia is not None and referencia != "":
                filtros = "%s AND productos.referencia = %s" % (filtros, referencia)

            # Obtener info del filtro (departamento)
            departamento = ""
            if auto_departamento is not None and auto_departamento != "":
                cursor.execute("SELECT auto, nombre FROM empresa_departamentos WHERE auto = %s", [auto_departamento])
                departamento = dictfetchall(cursor)[0]

                filtros = "%s AND productos.auto_departamento = %s" % (filtros, auto_departamento)

            # Obtener info del filtro (grupo)
            grupo = ""
            if auto_grupo is not None and auto_grupo != "":
                # Obtener e grupos/familias del filtro
                cursor.execute("SELECT auto, nombre FROM productos_grupo WHERE auto = %s", [auto_grupo])
                grupo = dictfetchall(cursor)[0]

                filtros = "%s AND productos.auto_grupo = %s" % (filtros, auto_grupo)

            marca = ""
            if auto_marca is not None and auto_marca != "":
            # Obtener la marcas del filtro
                cursor.execute("SELECT auto, nombre FROM productos_marca WHERE auto = %s", [auto_marca])
                marca = dictfetchall(cursor)[0]

                filtros = "%s AND productos.auto_marca = %s" % (filtros, auto_marca)

            if categoria is not None and categoria != "":
                filtros = "%s AND productos.categoria = '%s'" % (filtros, categoria)


            # Obtener los articulos
            sql_completo = sql + filtros + " GROUP BY auto"
            cursor.execute(sql_completo)
            articulos = dictfetchall(cursor)

            # Filtro de fechas para ventas
            filtro_ventas = request.POST.get("filtro-dias") # dias || fechas
            dias = 0
            desde = ""
            hasta = str(datetime.today().date()) # Por default hasta el dia de hoy

            # si es por dias (Hoy, dia anterior, ultimos 15 dias, etc)
            if filtro_ventas == "dias":
                dias = request.POST.get("filtro-dia")
                d = datetime.today() - timedelta(days=int(dias)) # Desde hoy descuenta los dias indicados
                desde = str(d.date()) # Lo pasamos a string
                if dias == "1": # Si la opcion es "Dia Anterior" solo mostramos los datos de ese dia especfico
                    hasta = desde
            elif filtro_ventas == "fechas": # Si es por rango de fechas
                desde = request.POST.get("filtro-desde")
                if request.POST.get("filtro-hasta") != "" and request.POST.get("filtro-hasta") is not None: # SI no se pasa una fecha es hasta hoy
                    hasta = request.POST.get("filtro-hasta")


            # Damos formato a los datos
            articulos_array = []
            for articulo in articulos:
                articulo_objeto = {
                    "codigo": articulo["codigo"],
                    "nombre": articulo["nombre"],
                    "usuarios": [],
                    "cantidad_vendida": 0,
                    "cantidad_depositos": 0.00
                }
             
                cursor.execute("SELECT ventas.usuario as nombre, SUM( ventas_detalle.cantidad ) AS cantidad FROM ventas_detalle INNER JOIN ventas ON ventas_detalle.auto_documento = ventas.auto WHERE ventas_detalle.auto_producto = %s AND ventas_detalle.fecha >= %s AND ventas_detalle.fecha <= %s GROUP BY ventas_detalle.nombre, ventas.usuario", [articulo["auto"], desde, hasta])
                # Ingresamos los datos al objeto del articulo
                usuarios = dictfetchall(cursor)

                for usuario in usuarios:                    
                    articulo_objeto["usuarios"].append(usuario)              

                cursor.execute("SELECT SUM(cantidad) as cantidad FROM ventas_detalle WHERE auto_producto = %s AND fecha >= %s AND fecha <= %s GROUP BY auto_producto", [articulo["auto"], desde, hasta])
                try:
                    cantidad = dictfetchall(cursor)[0]
                    articulo_objeto["cantidad_vendida"] = int(cantidad["cantidad"])
                except:
                    pass

                # Agregamos el articulo a la lista
                articulos_array.append(articulo_objeto)

            # Cerramos la conexion
            cursor.close()


        ctx        = {
            "company_id": company_id,
            "articulos": articulos_array,
            "proveedor": proveedor,
            "referencia": referencia,
            "departamento": departamento,
            "grupo": grupo,
            "marca": marca,
            "categoria": categoria,
            "fecha": str(datetime.today().date().strftime('%d-%m-%Y')),
            "desde":desde,
            "hasta":hasta
        }
        template   = "reportes/ventas/ventasUsuario-reporte-lista.html"
        return render(request, template, ctx)