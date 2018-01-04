from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.db import connection
import json

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class HomeView(View):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT auto, razon_social, ci_rif FROM proveedores WHERE estatus = 'Activo'")
            proveedores = dictfetchall(cursor)

            cursor.execute("SELECT auto, nombre FROM empresa_departamentos")
            departamentos = dictfetchall(cursor)

            cursor.execute("SELECT auto, nombre FROM productos_grupo")
            grupos = dictfetchall(cursor)

            cursor.close()

        ctx        = {
            "proveedores": proveedores,
            "departamentos": departamentos,
            "grupos": grupos

        }
        template   = "index.html"
        return render(request, template, ctx)

    def post(self, request):
        with connection.cursor() as cursor:
            # Obtener los articulos
            cursor.execute("SELECT productos.auto, productos.nombre FROM productos WHERE estatus = 'Activo' and codigo='01005'")
            articulos = dictfetchall(cursor)

            # Damos formato a los datos
            articulos_array = []
            for articulo in articulos:
                articulo_objeto = {
                    "nombre": articulo["nombre"],
                    "depositos": [],
                    "cantidad_vendida": 0
                }

                # Obtenemos los depositos
                cursor.execute("SELECT empresa_depositos.nombre, productos_deposito.fisica FROM productos_deposito INNER JOIN empresa_depositos ON productos_deposito.auto_deposito = empresa_depositos.auto WHERE productos_deposito.auto_producto = %s", [articulo["auto"]])
                # Ingresamos los datos al objeto del articulo
                depositos = dictfetchall(cursor)
                for deposito in depositos:
                    articulo_objeto["depositos"].append(deposito)

                # Calculamos las cantidades vendidas
                cursor.execute("SELECT cantidad FROM ventas_detalle WHERE codigo = '01005' and fecha > '2017-01-01'")
                cantidades = dictfetchall(cursor)
                c = 0
                for cantidad in cantidades:
                    c += cantidad["cantidad"]
                articulo_objeto["cantidad_vendida"] = int(c)

                # Agregamos el articulo a la lista
                articulos_array.append(articulo_objeto)

            # Cerramos la conexion
            cursor.close()
                

        ctx        = {
            "articulos": articulos_array
        }
        template   = "index.html"
        return render(request, template, ctx)