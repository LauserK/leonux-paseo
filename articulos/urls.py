from django.conf.urls import url
from .views import ArticuloReporteView, ReporteMenuView

urlpatterns = [
    # Reporte articulos
    url(r'^$', ReporteMenuView.as_view(), name='reporte-home'),
    url(r'^articulos/$', ArticuloReporteView.as_view(), name='reporte-articulos'),
]
