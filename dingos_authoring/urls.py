from django.conf.urls import patterns, url
from django.conf.urls.static import static
from os import path

from . import views

urlpatterns = patterns('dingos_authoring.views',
                       url(r'^$', views.index, name="dingos_authoring.index"),
                       url(r'^ref/$', views.ref, name="dingos_authoring.ref"),
                       )
