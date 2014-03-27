from django.conf.urls import patterns, url
from django.conf.urls.static import static
from os import path

from . import views

urlpatterns = patterns('dingos_authoring.views',
                       url(r'^$', views.index, name = "dingos_authoring.index"),
                       url(r'^Templates/CampaignIndicators/$', views.TemplateCampaignIndicators, name="dingos_authoring.template.campaign_indicators"),
                       url(r'^Templates/CampaignIndicators/transform$', views.transform.as_view(), name="dingos_authoring.template.campaign_indicators.transform"),
                       url(r'^Templates/CampaignIndicators/load$', views.GetDraftJSON.as_view(), name="dingos_authoring.load_json"),

                       url(r'^ref/$', views.ref.as_view(), name="dingos_authoring.ref"),
                       url(r'^XMLImport/$',
                           views.XMLImportView.as_view(),
                           name= "url.dingos_authoring.action.xml_import"),
                       )
