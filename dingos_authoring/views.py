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

import json, collections, logging, traceback
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from dingos.models import InfoObject
from django.db.models import Q
from django.utils import timezone

from django.contrib import messages

from django.contrib.auth.models import User, Group



from braces.views import LoginRequiredMixin, SuperuserRequiredMixin

from dingos.core.utilities import lookup_in_re_list
from dingos import DINGOS_INTERNAL_IOBJECT_FAMILY_NAME, DINGOS_TEMPLATE_FAMILY
from dingos.view_classes import BasicListView, BasicTemplateView, BasicJSONView, BasicFilterView

from dingos.importer import Generic_XML_Import



from models import GroupNamespaceMap

from django.views.generic import View
from transformer import stixTransformer

from .models import AuthoredData, GroupNamespaceMap

from .view_classes import AuthoringMethodMixin

import libxml2

from . import DINGOS_AUTHORING_IMPORTER_REGISTRY

#from libmantis import *
#from mantis_client import utils

from forms import XMLImportForm

import forms as observables
from operator import itemgetter

import sys

import pkgutil



logger = logging.getLogger(__name__)






class index(BasicListView):
    """
    Overview of saved drafts.
    """
    title = "Saved Drafts"
    template_name = 'dingos_authoring/%s/AuthoredObjectList.html' % DINGOS_TEMPLATE_FAMILY

    @property
    def queryset(self):
        return AuthoredData.objects.filter(kind=AuthoredData.AUTHORING_JSON,
                                           user=self.request.user,
                                           status=AuthoredData.DRAFT).order_by('name').distinct('name')


class transform(LoginRequiredMixin,AuthoringMethodMixin,View):

    processor = "http://stix.mitre.org/stix"
    display_view = 'dingos_authoring.template.campaign_indicators'

    def post(self, request, *args, **kwargs):
        res = {}
        if True: #try:
            POST = request.POST
            jsn = ''
            if POST.has_key(u'jsn'):
                jsn = POST[u'jsn']
                submit_name = POST[u'submit_name']
                submit_action = POST.get(u'action','import')
                try:
                    namespace_info = self.get_authoring_namespaces()
                except StandardError, e:
                    return HttpResponse(json.dumps({'msg':e.message}), content_type="application/json")



                AuthoredData.object_update_or_create(current_kind=AuthoredData.AUTHORING_JSON,
                                                     current_user=self.request.user,
                                                     current_name= submit_name,
                                                     current_timestamp='latest',
                                                     status=AuthoredData.DRAFT,
                                                     processor='test',
                                                     display_view=self.display_view,
                                                     data = jsn)

                t = stixTransformer(jsn=jsn,
                                    namespace_uri=namespace_info['default_ns_uri'],
                                    namespace_slug=namespace_info['default_ns_slug'],)
                stix = t.getStix()

                if not stix:
                    return HttpResponse('{}', content_type="application/json")

                res['xml'] = stix
        #except Exception, e:
        #    res['msg'] = "An error occured: %s" % e.message
        #    logger.error("Authoring attempt resulted in error %s, traceback %s" % (e.message,traceback.format_exc()))
        #    raise e

        return HttpResponse(json.dumps(res), content_type="application/json")


class ref(BasicListView):
    def get_queryset(self):

        if self.request.method == u'GET':
            GET = self.request.GET
            if GET.has_key(u'type') and GET.has_key(u'q'):
                q = GET[u'q']
                t = GET[u'type']

                t_q = Q(iobject_type__name__icontains=t)
                t_q = Q(iobject_type__name__icontains='file')
                q_q = Q(identifier__uid__icontains=q) | Q(name__icontains=q)

                #TODO: check t and q for validity
                return InfoObject.objects.exclude(latest_of=None)\
                               .exclude(iobject_family__name__exact=DINGOS_INTERNAL_IOBJECT_FAMILY_NAME)\
                               .prefetch_related(
                                   'iobject_type',
                                   'iobject_family',
                                   'iobject_family_revision',
                                   'identifier')\
                               .filter(q_q)\
                               .filter(t_q)\
                               .select_related().distinct().order_by('-latest_of__pk')[:10]

        # Safetynet
        return InfoObject.objects.none()

    def render_to_response(self, context):
        #return self.get_json_response(json.dumps(context['object'].show_elements(""),indent=2))

        res = {'success': True,
               'result': map(
                   lambda x : {'id': x.identifier.uid, 'name': x.name, 'cat': str(x.iobject_type)},
                   context['object_list'])
        }
        return self.get_json_response(json.dumps(res))

    def get_json_response(self, content, **httpresponse_kwargs):
        return HttpResponse(content,
                            content_type='application/json',
                            **httpresponse_kwargs)



class GetDraftJSON(BasicJSONView):
    """
    View serving latest draft of given name
    """
    @property
    def returned_obj(self):

        name = self.request.GET.get('name',False)

        json_obj_l = AuthoredData.objects.filter(kind=AuthoredData.AUTHORING_JSON,
                                                 user=self.request.user,
                                                 #name= name,
                                                 status=AuthoredData.DRAFT).order_by('-timestamp')[:1]
        json_obj = json_obj_l[0].data

        print 'jsn %s' % json_obj
        return {'msg':'Loaded',
                'jsn':json_obj}

class XMLImportView(SuperuserRequiredMixin,BasicTemplateView):
    """
    View for importing XML.
    """

    template_name = 'dingos_authoring/%s/XMLImport.html' % DINGOS_TEMPLATE_FAMILY
    title = 'Import XML'

    def get_context_data(self, **kwargs):
        context = super(XMLImportView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

    def get(self, request, *args, **kwargs):
        self.form = XMLImportForm()
        return super(BasicTemplateView,self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = XMLImportForm(request.POST.dict())

        if self.form.is_valid():
            data = self.form.cleaned_data
            doc = libxml2.parseDoc(data['xml'])
            root = doc.getRootElement()

            ns_mapping = {}
            try:
                ns_def = root.nsDefs()

                while ns_def:
                    ns_mapping[ns_def.name] = ns_def.content
                    ns_def = ns_def.next
            except:
                pass


            try:
                ns_slug = root.ns().name
            except:
                ns_slug = None

            if ns_slug:
                namespace = ns_mapping.get(ns_slug,None)
            else:
                namespace = ''

            importer_class = Generic_XML_Import

            importer_class = lookup_in_re_list(DINGOS_AUTHORING_IMPORTER_REGISTRY,namespace)

            if not importer_class:
                messages.error(self.request,"Do not know how to import XML with namespace '%s'" % (namespace))
            else:
                importer = importer_class()
                result = importer.xml_import(xml_content = data['xml'])
                messages.success(self.request,"Submitted %s" % (namespace))

        return super(BasicTemplateView,self).get(request, *args, **kwargs)


