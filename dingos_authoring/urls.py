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

from django.conf.urls import url
from django.conf.urls.static import static
from os import path

from . import views


urlpatterns = [
    url(r'^$', views.index.as_view(), name="url.dingos_authoring.index"),

    url(r'^History$', views.index.as_view(), name="url.dingos_authoring.index"),
    url(r'^History/(?P<id>[^/]*)/$', views.AuthoredDataHistoryView.as_view(), name="url.dingos_authoring.view.authored_object.history"),

    # The XML import page
    url(r'^XMLImport/$', views.XMLImportView.as_view(), name= "dingos_authoring.action.xml_import"),
    # The Test GUI JSON Import page
    url(r'^GUIJSONImport/$', views.GUI_JSON_ImportTest.as_view(), name= "dingos_authoring.action.gui_json_import"),

    url(r'^Imports$', views.ImportsView.as_view(), name="url.dingos_authoring.imports"),
    url(r'^Action/_take_reports$', views.TakeReportView.as_view(), name="url.dingos_authoring.index.action.take"),
    url(r'^Action/SwitchAuthoringGroup$', views.SwitchAuthoringGroupView.as_view(), name="url.dingos_authoring.action.switch_authoring_group"),


    # Cross-authoring-app functionality
    url(r'^load$', views.GetDraftJSON.as_view(), name="url.dingos_authoring.load_json"),
    url(r'/load$', views.GetDraftJSON.as_view(), name="url.dingos_authoring.load_json"),
    url(r'^ping$', views.Ping.as_view(), name="url.dingos_authoring.ping"),
    url(r'/ping$', views.Ping.as_view(), name="url.dingos_authoring.ping"),

    url(r'/get_namespace$', views.GetAuthoringNamespace.as_view(), name="url.dingos_authoring.get_namespace"),

    url(r'Test/Celery', views.CeleryTest.as_view())

]

