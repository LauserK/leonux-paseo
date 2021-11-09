# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import View
from django.shortcuts import render
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection, connections
from .models import Article, Configuration, MovementReason, MovementArticle
from datetime import datetime

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

# Create your views here.
class MigrateView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        ctx = {}
        template   = "menus/migrate.html"
        return render(request, template, ctx)

    def post(self, request):
        cursor = connections['celestes'].cursor()  
        with cursor:
            articles = Article.objects.filter(isForSell=True)
            for article in articles:                
                if article.barcode:
                    percentage = Configuration.objects.get(pk=1).taxPercentage
                    price_without_iva = Decimal(article.sellPrice) / ((percentage + Decimal(100)) / Decimal(100))
                    cursor.execute("UPDATE productos SET precio_1 = %s WHERE codigo = %s" % (str(price_without_iva), article.barcode))                    
            cursor.close()
    	ctx = {
    		"msg": "Realizado"
    	}
        template   = "menus/migrate.html"
    	return render(request, template, ctx)

class CalculateInventoryView(LoginRequiredMixin, View):
    def get(self, request):
        ctx = {}
        template = "menus/inventory.html"
        return render(request, template, ctx)

    def post(self, request):
        cursor = connections['celestes'].cursor()  
        fecha = request.POST.get("filtro-fecha")
        articles_not_updated = []
        articles_updated = []

        with cursor:
            cursor.execute("SELECT codigo, nombre, cantidad FROM ventas_detalle WHERE fecha = %s", [fecha])
            articulos = dictfetchall(cursor)

            for articulo in articulos:
                #print articulo["codigo"]
                article = Article.objects.filter(barcode=articulo["codigo"]).first()
                if article:
                    article = {
                        "name": articulo['nombre'],
                        "code": articulo['codigo'],
                        "quantity": articulo['cantidad']
                    }
                    articles_updated.append(article)
                else:
                    article = {
                        "name": articulo['nombre'],
                        "code": articulo['codigo']
                    }
                    articles_not_updated.append(article)

            cursor.close()   


        # make update
        if articles_updated > 0:
            date = datetime.strptime(fecha, "%Y-%m-%d")           
            MovementArticle.objects.filter(date=date).delete()

            movimiento = MovementReason.objects.get(pk=4)            
            for article in articles_updated:
                article_django = Article.objects.get(barcode=article["code"])  
                quantity = article['quantity']                

                movement = MovementArticle()
                movement.article = article_django
                movement.sign = '-'
                movement.quantity = quantity
                movement.reason = movimiento
                movement.date = date
                movement.save()

                print "-----------------------"
                print "------- ARTICLE -------"
                print "--%s--" % article_django.name
                print "-----------------------"

                """
                #ingredientes menos
                for ingrediente in article_django.ingredients.all():
                    movement = MovementArticle()
                    movement.article = ingrediente.article
                    movement.sign = sign
                    movement.quantity = ingrediente.quantity
                    movement.reason = movimiento
                    movement.date = date
                    movement.save()                    

                    for ingredient1 in ingrediente.article.ingredients.all():
                        print "hello"
                        movement = MovementArticle()
                        movement.article = ingredient1.article
                        movement.sign = sign
                        movement.quantity = ingredient1.quantity
                        movement.reason = movimiento
                        movement.date = date
                        movement.save()
                """
                    
            """
            # Actualizar storage
            articles = Article.objects.all()

            for article in articles:
                movements = MovementArticle.objects.filter(article=article)
                total = Decimal(0.00)

                for movement in movements:
                    if movement.sign == "+":
                        total += Decimal(movement.quantity)
                    else:
                        total -= Decimal(movement.quantity)

                article.storageQuantity = total
                article.save()
            """

        ctx = {
            "msg": "Realizado",
            "cant_articles_not_updated": len(articles_not_updated),
            "articles_not_updated": articles_not_updated
        }
        template = "menus/inventory.html"
        return render(request, template, ctx)