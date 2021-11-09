from django.conf.urls import url
from .views import MigrateView, CalculateInventoryView


urlpatterns = [
    # Reporte articulos
    url(r'^migrate/$', MigrateView.as_view(), name='migrate'),
    url(r'^calculate/$', CalculateInventoryView.as_view(), name='calculate'),
    #url(r'^$', ReporteCompanyView.as_view(), name='reporte-company'),
    #url(r'^$', ReporteMenuView.as_view(), name='reporte-home'),
    #url(r'^articulos/$', ArticuloReporteView.as_view(), name='reporte-articulos'),
    #url(r'^ventas/$', VentasReporteView.as_view(), name='reporte-ventas'),
    #url(r'^ventas-usuario/$', VentaUsuarioReporteView.as_view(), name='reporte-ventas'),
]
