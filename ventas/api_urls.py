from django.conf.urls import url
from .api import Stations, Devices, Sessions, Tickets, Report
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # API VENTAS URLS    
    url(r'^stations/$', Stations.as_view(), name='stations-api'),
    url(r'^stations/(?P<station_id>\d+)/close/$', csrf_exempt(Report.as_view()), name='report-api'),
    url(r'^stations/(?P<station_id>\d+)/devices/$', Devices.as_view(), name='devices-api'),
    url(r'^stations/(?P<station_id>\d+)/session/$', Sessions.as_view(), name='sessions-api'),
    url(r'^stations/(?P<station_id>\d+)/session/tickets/(?P<ticket_number>\d+)/$', Tickets.as_view(), name='sessions-tickets-api'),
]
