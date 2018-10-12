from django.conf.urls import url
from .api import Sections, Stations, Devices, Sessions, Tickets, Report, Groups, Articles, AddArticleAccount, RemoveArticleAccount, RemoveAllArticleAccount, GetAllArticlesAccount, GetClientByQueue, UpdateClientStatus, UpdateClientSection, UpdateArticleQuantity, GenerateMovementDocument

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # API VENTAS URLS    
    url(r'^stations/$', Stations.as_view(), name='stations-api'),
    url(r'^stations/(?P<station_id>\d+)/close/$', csrf_exempt(Report.as_view()), name='report-api'),
    url(r'^stations/(?P<station_id>\d+)/devices/$', Devices.as_view(), name='devices-api'),
    url(r'^stations/(?P<station_id>\d+)/session/$', Sessions.as_view(), name='sessions-api'),
    url(r'^stations/(?P<station_id>\d+)/session/tickets/(?P<ticket_number>\d+)/$', Tickets.as_view(), name='sessions-tickets-api'),

    # POS IOS
    url(r'^sections/$', csrf_exempt(Sections.as_view()), name='sections-api'),
    url(r'^clients/$', csrf_exempt(GetClientByQueue.as_view()), name='clients-api'),
    url(r'^clients/update-section/$', csrf_exempt(UpdateClientSection.as_view()), name='clientss-api'),
    url(r'^clients/update/$', csrf_exempt(UpdateClientStatus.as_view()), name='clients-api'),
    url(r'^groups/$', csrf_exempt(Groups.as_view()), name='groups-api'),
    url(r'^articles/$', csrf_exempt(Articles.as_view()), name='articles-api'),
    url(r'^articles/account/$', csrf_exempt(GetAllArticlesAccount.as_view()), name='articles-api'),
    url(r'^articles/add/$', csrf_exempt(AddArticleAccount.as_view()), name='articles-api'),
    url(r'^articles/updateQuantity/$', csrf_exempt(UpdateArticleQuantity.as_view()), name='articles-api'),
    url(r'^articles/remove/$', csrf_exempt(RemoveArticleAccount.as_view()), name='articles-api'),
    url(r'^articles/remove/all/$', csrf_exempt(RemoveAllArticleAccount.as_view()), name='articles-api'),
    url(r'^articles/movement/$', csrf_exempt(GenerateMovementDocument.as_view()), name="articles-movements")
]
