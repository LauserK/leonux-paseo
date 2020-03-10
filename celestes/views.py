# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import View
from django.shortcuts import render
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection, connections
from .models import Article, Configuration

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

    	ctx = {
    		"msg": "Realizado"
    	}
        template   = "menus/migrate.html"
    	return render(request, template, ctx)