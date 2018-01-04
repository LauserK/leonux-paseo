from django.conf.urls import url
from .views import HomeView

urlpatterns = [
    # Lista de clientes (Datos desde Servicios) (Home)
    url(r'^$', HomeView.as_view(), name='clientes_list'),
]
