from django.conf.urls import url
from .views import HomeView, EstacionesView, EstacionesEditView, EstacionesAddView, EstacionesDestroyView

urlpatterns = [
    # Home ventas
    url(r'^$', HomeView.as_view(), name='home'),

    # Estacion lista
    url(r'^estaciones/$', EstacionesView.as_view(), name='estaciones'),
    url(r'^estaciones/(?P<estacion_id>\d+)/$', EstacionesEditView.as_view(), name='estaciones-edit'),
    url(r'^estaciones/(?P<estacion_id>\d+)/delete/$', EstacionesDestroyView.as_view(), name='estaciones-delete'),
    url(r'^estaciones/agregar/$', EstacionesAddView.as_view(), name='estaciones-add'),
]
