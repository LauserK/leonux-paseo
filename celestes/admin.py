# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import Article, MovementReason, MovementArticle, Currency, Configuration, Ingredient, DocumentMovement, ArticleType

class IngredientInline(admin.TabularInline):
    model = Article.ingredients.through
    verbose_name = u"Ingredient"
    verbose_name_plural = u"Ingredients"

class MovementInline(admin.TabularInline):
    model = DocumentMovement.movements.through
    verbose_name = u"Movement"
    verbose_name_plural = u"Movements"

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    exclude = ("ingredients",)
    inlines = (
       IngredientInline,
    )
    ordering = ('name',)
    list_display = ('name', 'barcode', 'costPrice', 'sellPrice', 'isForSell', 'article_type')
    list_filter = ('article_type',)

@admin.register(DocumentMovement)
class DocumentMovementAdmin(admin.ModelAdmin):
    exclude = ("movements",)
    inlines = (
       MovementInline,
    )    

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass

@admin.register(MovementReason)
class MovementReasonAdmin(admin.ModelAdmin):
    pass

@admin.register(MovementArticle)
class MovementArticleAdmin(admin.ModelAdmin):
    pass

@admin.register(Currency)
class CurrencyArticleAdmin(admin.ModelAdmin):
    pass

@admin.register(Configuration)
class ConfigurationArticleAdmin(admin.ModelAdmin):
    pass

@admin.register(ArticleType)
class ArticleTypeAdmin(admin.ModelAdmin):
    pass