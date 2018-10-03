from django.conf.urls import url
from .views import ArticuloReporteView, ReporteMenuView, VentasReporteView, VentaUsuarioReporteView

urlpatterns = [
    # Reporte articulos
    url(r'^$', ReporteMenuView.as_view(), name='reporte-home'),
    url(r'^articulos/$', ArticuloReporteView.as_view(), name='reporte-articulos'),
    url(r'^ventas/$', VentasReporteView.as_view(), name='reporte-ventas'),
    url(r'^ventas-usuario/$', VentaUsuarioReporteView.as_view(), name='reporte-ventas'),
]
