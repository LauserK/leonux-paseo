# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from decimal import Decimal
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from datetime import datetime
import math 

class Ingredient(models.Model):
	article = models.ForeignKey('Article')
	quantity = models.DecimalField(default=1, max_digits=12, decimal_places=3)

	def __unicode__(self):
		ingredientCostPrice = (self.article.costPrice / self.article.packageQuantity)			
		ingredientPrice = ingredientCostPrice * self.quantity
		return "%s:%s - Cantidad: %s - Bs: %s" % (self.article.name, str(self.article.costPrice), str(self.quantity), str(ingredientPrice))    

class ArticleType(models.Model):
	name = models.CharField(max_length=50)

	def __unicode__(self):
		return self.name

DEFAULT_ARTICLE_TYPE = 1
class Article(models.Model):
	barcode = models.CharField(max_length=30, help_text='Codigo usado para conectarse a leonux y hacer cambios al articulo', blank=True, null=True)
	name = models.CharField(max_length=100)
	article_type = models.ForeignKey(ArticleType, default=DEFAULT_ARTICLE_TYPE)
	storageQuantity = models.DecimalField(default=0.00, max_digits=11, decimal_places=2)
	costPrice = models.DecimalField(default=0.00, max_digits=11, decimal_places=2)
	packageQuantity = models.DecimalField(default=1000, max_digits=11, decimal_places=2, help_text='Monto para realizar el calculo del precio del gr del articulo (CostPrice)/(PackageQuantity)')
	percentageProfit = models.IntegerField(default=50)
	sellPrice = models.DecimalField(default=0, max_digits=11, decimal_places=2)
	ingredients = models.ManyToManyField(Ingredient, blank=True, related_name='article_ingredient')    
	secondaryPrice = models.DecimalField(default=0.00, max_digits=11, decimal_places=2)
	isForSell = models.BooleanField(default=False, help_text='El Articulo es para la venta?')
	cookingTime = models.IntegerField(blank=True, default=0, help_text='Tiempo de coccion en segundos')

	def __unicode__(self):
		return self.name

class MovementReason(models.Model):
	name = models.CharField(max_length=100)

	def __unicode__(self):
		return self.name

class MovementArticle(models.Model):
	article = models.ForeignKey(Article)
	sign = models.CharField(max_length=1, default='+', help_text='"+" para sumar | "-" para restar')
	quantity = models.DecimalField(default=0.00, max_digits=11, decimal_places=2)
	reason = models.ForeignKey(MovementReason)
	date = models.DateField(blank=True, default=datetime.now)

	def __unicode__(self):
		return "%s sign: %s q: %d" % (self.article.name, self.sign, self.quantity)

class DocumentMovement(models.Model):
	date = models.DateField(default=datetime.now)
	movements = models.ManyToManyField(MovementArticle, blank=True)	

class Currency(models.Model):
	name = models.CharField(max_length=20)
	currencyBased = models.ForeignKey('self', blank=True, null=True)
	pointBased = models.DecimalField(default=0.00,max_digits=11, decimal_places=2)

	def __unicode__(self):
		return self.name

class Configuration(models.Model):
	primaryCurrency = models.ForeignKey(Currency)
	secondaryCurrency = models.ForeignKey(Currency, related_name='config_currency', blank=True, null=True)
	roundPriceBy = models.DecimalField(default=500.00,max_digits=11, decimal_places=2)
	taxPercentage = models.DecimalField(default=16.00,max_digits=6, decimal_places=2)

# method for updating Article
@receiver(pre_save, sender=Article, dispatch_uid="save_article")
def update_article(sender, instance, **kwargs):		
	dollarPrice = Configuration.objects.get(pk=1).secondaryCurrency.pointBased
	priceArticle = instance.secondaryPrice
	price = 0

	# Precio de costo en base al dolar
	if priceArticle > 0:
		price = dollarPrice * priceArticle		
		if price != 0:
			instance.costPrice = price			
			
	# Actualizar precio en base a sus ingredientes
	if instance.pk:
		costPrice = 0
		if len(instance.ingredients.all()) > 0:
			#costPrices
			for ingredient in instance.ingredients.all():
				ingredientCostPrice = (ingredient.article.costPrice / ingredient.article.packageQuantity)			
				ingredientPrice = ingredientCostPrice * ingredient.quantity
				costPrice += ingredientPrice								
			instance.costPrice = costPrice

	# Actualizar precio de venta
	if instance.costPrice != 0 or price != 0:	
		# Get tax
		config = Configuration.objects.get(pk=1)
		if price == 0:
			price = instance.costPrice		
		factor = Decimal((instance.percentageProfit+100)) / Decimal(100)		
		price = price * factor	
		# precio de venta con impuesto
		price_with_tax = price * ((config.taxPercentage+100)/ Decimal(100))
		instance.sellPrice = -(-price_with_tax//config.roundPriceBy)*config.roundPriceBy

	# Actualizar precios de articulos que contengan a este como ingrediente
	article_based = instance.pk #obtengo el articulo que se actualizo
	# busco ingredientes con ese articulo
	ingredients_with_article = Ingredient.objects.filter(article=article_based)	
	# busco Articulos con los ingredientes que busque anteriormente
	articles_with_ingredients = Article.objects.filter(ingredients__in=ingredients_with_article).distinct()
	# recorrer articulos
	for article in articles_with_ingredients:
		# update price 
		#print"------- "+ article.name +" ---------"
		costPrice = 0
		if len(article.ingredients.all()) > 0:
			for ingredient in article.ingredients.all():
				ingredientCostPrice2 = ingredient.article.costPrice
				ingredientPackageQuantity = ingredient.article.packageQuantity
				ingredientQuantity = ingredient.quantity

				if ingredient.article.pk == instance.pk:					
					ingredientCostPrice2 = instance.costPrice
					ingredientPackageQuantity = instance.packageQuantity					

				ingredientCostPrice = (ingredientCostPrice2 / ingredientPackageQuantity)			
				ingredientPrice = ingredientCostPrice * ingredientQuantity
				costPrice += ingredientPrice
				"""
				print "ingredientName: " + ingredient.article.name
				print "ingredientCostPrice2: " + str(ingredientCostPrice2)
				print "ingredientPackageQuantity: " + str(ingredientPackageQuantity)
				print "ingredientQuantity: " + str(ingredientQuantity)
				print "ingredientCostPrice: " + str(ingredientCostPrice)
				print "ingredientPrice: " + str(ingredientPrice)"""
		#print "costPrice: " + str(costPrice)
		#print"-----------------------"

		article.costPrice = costPrice


		config = Configuration.objects.get(pk=1)					
		factor = Decimal((article.percentageProfit+100)) / Decimal(100)		
		price = costPrice * factor	
		# precio de venta con impuesto
		price_with_tax = price * ((config.taxPercentage+100)/ Decimal(100))
		article.sellPrice = -(-price_with_tax//config.roundPriceBy)*config.roundPriceBy

		article.save()

# method for updating Article
@receiver(post_save, sender=Currency, dispatch_uid="save_currency")
def update_currency(sender, instance, **kwargs):
	# instance.pointBased	
	dollarPrice = instance.pointBased	


	if dollarPrice > 0:
		# actualizar precio de costos basados en dolares
		articles = Article.objects.all()

		for article in articles:
			if article.secondaryPrice > 0:
				article.costPrice = article.secondaryPrice * dollarPrice

			article.save()

		for article in articles:
			if article.secondaryPrice > 0:
				# busco ingredientes con ese articulo
				ingredients_with_article = Ingredient.objects.filter(article=article)	
				# busco Articulos con los ingredientes que busque anteriormente
				articles_with_ingredients = Article.objects.filter(ingredients__in=ingredients_with_article).distinct()
				# recorrer articulos
				for article in articles_with_ingredients:
					# update price 
					print"------- "+ article.name +" ---------"
					costPrice = 0
					if len(article.ingredients.all()) > 0:
						for ingredient in article.ingredients.all():
							ingredientCostPrice2 = ingredient.article.costPrice
							ingredientPackageQuantity = ingredient.article.packageQuantity
							ingredientQuantity = ingredient.quantity											

							ingredientCostPrice = (ingredientCostPrice2 / ingredientPackageQuantity)			
							ingredientPrice = ingredientCostPrice * ingredientQuantity
							costPrice += ingredientPrice
							"""
							print "ingredientName: " + ingredient.article.name
							print "ingredientCostPrice2: " + str(ingredientCostPrice2)
							print "ingredientPackageQuantity: " + str(ingredientPackageQuantity)
							print "ingredientQuantity: " + str(ingredientQuantity)
							print "ingredientCostPrice: " + str(ingredientCostPrice)
							print "ingredientPrice: " + str(ingredientPrice)"""
					print "costPrice: " + str(costPrice)
					print"-----------------------"

					article.costPrice = costPrice

					# Get tax
					config = Configuration.objects.get(pk=1)					
					factor = Decimal((article.percentageProfit+100)) / Decimal(100)		
					price = costPrice * factor	
					# precio de venta con impuesto
					price_with_tax = price * ((config.taxPercentage+100)/ Decimal(100))
					article.sellPrice = -(-price_with_tax//config.roundPriceBy)*config.roundPriceBy

					article.save()

@receiver(post_save, sender=MovementArticle, dispatch_uid="save_movements")
def update_movement_article(sender, instance, **kwargs):
	article = instance.article
	movements = MovementArticle.objects.filter(article=article)
	movimiento = MovementReason.objects.get(pk=4)
	ARTICLE_TYPE_SERVICE = ArticleType.objects.get(pk=5)
	ARTICLE_TYPE_FINAL_PRODUCT = ArticleType.objects.get(pk=3)
	total = Decimal(0.00)

	# Make movements
	if instance.sign == "+":
		# Sumando	

		"""
		Al sumar a un articulo compuesto quiere decir que fue producido, osea se necesita disminuir 
		el inventario usado para la produccion, a a restar los ingredientes unicamente cuando sea 
		un articulo final y su almacenamiento sea mayor o igual a 0, ya que cuando es negativo quiere 
		decir que ya se descontaron los ingredientes anteriormente
		"""
		if article.article_type == ARTICLE_TYPE_FINAL_PRODUCT and article.storageQuantity >= 0:
			for ingrediente in article.ingredients.all():
				if ingrediente.article.article_type != ARTICLE_TYPE_SERVICE:				
					movement = MovementArticle()
					movement.article = ingrediente.article
					movement.sign = '-'
					movement.quantity = ingrediente.quantity * Decimal(instance.quantity)
					movement.reason = movimiento
					movement.date = instance.date
					movement.save() 
	else:
		# Restando
		if article.storageQuantity <= 0:
			for ingrediente in article.ingredients.all():
				if ingrediente.article.article_type != ARTICLE_TYPE_SERVICE:
					movement = MovementArticle()
					movement.article = ingrediente.article
					movement.sign = '-'
					movement.quantity = ingrediente.quantity * Decimal(instance.quantity)
					movement.reason = movimiento
					movement.date = instance.date
					movement.save()    

	# Caculate inventories
	for movement in movements:
		if movement.sign == "+":
			total += Decimal(movement.quantity)
		else:
			total -= Decimal(movement.quantity)

	article.storageQuantity = total
	article.save()
	print "Guardado"