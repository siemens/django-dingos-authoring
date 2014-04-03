# Copyright (c) Siemens AG, 2014
#
# This file is part of MANTIS.  MANTIS is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either version 2
# of the License, or(at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#



from django.conf.urls import patterns, url
from django.conf.urls.static import static
from os import path

from . import views

from transformers.stix.CampaignIndicators import FormView as CampaingIndicatorsFormView
from transformers.stix.CampaignIndicators import ProcessingView as CampaingIndicatorsProcessingView
from transformers.stix.CampaignIndicators import FORM_VIEW_NAME as CampaingIndicatorsViewName



urlpatterns = patterns('dingos_authoring.views',
                       url(r'^$', views.index.as_view(), name = "dingos_authoring.index"),

                       url(r'^Templates/CampaignIndicators/$', CampaingIndicatorsFormView.as_view(), name=CampaingIndicatorsViewName),
                       url(r'^Templates/CampaignIndicators/transform$', CampaingIndicatorsProcessingView.as_view()),
                       url(r'^Templates/CampaignIndicators/load$', views.GetDraftJSON.as_view(), name="dingos_authoring.load_json"),

                       url(r'^ref/$', views.ref.as_view(), name="dingos_authoring.ref"),

                       url(r'^XMLImport/$',
                           views.XMLImportView.as_view(),
                           name= "url.dingos_authoring.action.xml_import"),
                       )
