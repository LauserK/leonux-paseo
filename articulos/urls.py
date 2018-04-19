from django.conf.urls import url
from .views import ArticuloReporteView

urlpatterns = [
    # Reporte articulos
    url(r'^articulos/$', ArticuloReporteView.as_view(), name='reporte-articulos'),
]
