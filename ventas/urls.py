from django.conf.urls import url
from .views import HomeView, EstacionesView, EstacionesEditView, EstacionesAddView, EstacionesDestroyView, DispositivoView, DispositivoEditView, DispositivoAddView, DispositivoDestroyView, PlatcoCSVAddView, JornadaVerifyView

urlpatterns = [
    # Home ventas
    url(r'^$', HomeView.as_view(), name='home'),
    # Subir CSV Platco
    url(r'^csv/upload/$', PlatcoCSVAddView.as_view(), name='upload-csv'),
    # Verificar jornada
    url(r'^jornada/verify/$', JornadaVerifyView.as_view(), name='jornada-verify'),

    # Estacion
    url(r'^estaciones/$', EstacionesView.as_view(), name='estaciones'),
    url(r'^estaciones/(?P<estacion_id>\d+)/$', EstacionesEditView.as_view(), name='estaciones-edit'),
    url(r'^estaciones/(?P<estacion_id>\d+)/delete/$', EstacionesDestroyView.as_view(), name='estaciones-delete'),
    url(r'^estaciones/agregar/$', EstacionesAddView.as_view(), name='estaciones-add'),

    # Dispositivos Punto de Venta
    url(r'^dispositivos/$', DispositivoView.as_view(), name='dispositivos'),
    url(r'^dispositivos/(?P<dispositivo_id>\d+)/$', DispositivoEditView.as_view(), name='dispositivos-edit'),
    url(r'^dispositivos/(?P<dispositivo_id>\d+)/delete/$', DispositivoDestroyView.as_view(), name='dispositivos-delete'),
    url(r'^dispositivos/agregar/$', DispositivoAddView.as_view(), name='dispositivos-add'),
]
