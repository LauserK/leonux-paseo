"""leonux_paseo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
from articulos import urls as articulos_urls
from celestes import urls as celestes_urls
from ventas import api_urls as ventas_api_urls, urls as ventas_urls
from django.contrib.auth import urls as auth_urls
from articulos.views import ReporteCompanyView, ReporteMenuView
from usuarios.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', ReporteCompanyView.as_view(), name='home'),
    url(r'^(?P<company_id>\d+)/$', ReporteMenuView.as_view(), name='home'),
    url(r'^(?P<company_id>\d+)/reportes/', include(articulos_urls, namespace='reportes')),
    url(r'^ventas/cierres/', include(ventas_urls, namespace='ventas')),
    url(r'^accounts/', include(auth_urls)),
    url(r'^celestes/', include(celestes_urls, namespace='celestes')),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^admin/', admin.site.urls),

    # API URLS
    url(r'^api/v1/ventas/', include(ventas_api_urls, namespace='api_ventas')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)