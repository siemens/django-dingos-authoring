from django.conf.urls import patterns, url
from django.conf.urls.static import static
from os import path

from . import views

urlpatterns = patterns('dingos_authoring.views',
                       url(r'^$', views.index, name="dingos_authoring.index"),
                       url(r'^transform$', views.transform.as_view(), name="dingos_authoring.transform"),
                       url(r'^ref/$', views.ref.as_view(), name="dingos_authoring.ref"),
                       url(r'^XMLImport/$',
                           views.XMLImportView.as_view(),
                           name= "url.dingos_authoring.action.xml_import"),
                       )
