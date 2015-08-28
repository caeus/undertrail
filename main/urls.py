__author__ = 'Caeus'
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search_tickets$', views.SearchTickets.as_view(), name='search_tickets'),
]
