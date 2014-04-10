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

import json, collections, logging, traceback, re
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
from lxml import etree
from base64 import b64encode

from . import DINGOS_AUTHORING_IMPORTER_REGISTRY

#from libmantis import *
#from mantis_client import utils

from forms import XMLImportForm

import forms as observables
from operator import itemgetter
import hashlib

import sys

import pkgutil



logger = logging.getLogger(__name__)

import importlib

AUTHORING_IMPORTER_REGISTRY = []

for (matcher,module,class_name) in DINGOS_AUTHORING_IMPORTER_REGISTRY:
    my_module = importlib.import_module(module)
    AUTHORING_IMPORTER_REGISTRY.append((matcher,getattr(my_module,class_name)))



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
    View serving latest draft of given name, or respond with the list of available templates
    """
    @property
    def returned_obj(self):
        res = {
            'status': False,
            'msg': 'An error occured loading the requested template',
            'data': None
        }

        if 'list' in self.request.GET:
            json_obj_l = AuthoredData.objects.filter(kind=AuthoredData.AUTHORING_JSON,
                                                     user=self.request.user,
                                                     status=AuthoredData.DRAFT).order_by('-timestamp')
            res['status'] = True
            res['msg'] = ''
            res['data'] = []
            for el in json_obj_l:
                res['data'].append({'id': el.identifier.name, 'name': el.name})

        else:
            name = self.request.GET.get('name',False)
            json_obj_l = AuthoredData.objects.filter(kind=AuthoredData.AUTHORING_JSON,
                                                     user=self.request.user,
                                                     identifier__name=name,
                                                     status=AuthoredData.DRAFT).order_by('-timestamp')[:1]

            try:
                res['data'] = {}
                res['data']['jsn'] = json_obj_l[0].data
                res['data']['name'] = json_obj_l[0].name
                res['data']['id'] = json_obj_l[0].identifier.name
                res['status'] = True
                res['msg'] = 'Loaded template \'' + json_obj_l[0].name + '\''
            except:
                pass

        return res


class XMLImportView(AuthoringMethodMixin,SuperuserRequiredMixin,BasicTemplateView):
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
            try:
                namespace_info = self.get_authoring_namespaces(self.request.user)
            except StandardError, e:
                messages.error(self.request,e.message)
                return super(XMLImportView,self).get(request, *args, **kwargs)

            importer_class = Generic_XML_Import

            importer_class = lookup_in_re_list(AUTHORING_IMPORTER_REGISTRY,namespace)

            if not importer_class:
                messages.error(self.request,"Do not know how to import XML with namespace '%s'" % (namespace))
            else:



                importer = importer_class(allowed_identifier_ns_uris=namespace_info['allowed_ns_uris'],
                                               default_identifier_ns_uri=namespace_info['default_ns_uri'],
                                               substitute_unallowed_namespaces=True)

                result = importer.xml_import(xml_content = data['xml'],
                                             track_created_objects=True)

                self.form = XMLImportForm()


                messages.success(self.request,"Imported objects: %s" % ", ".join(map(lambda x: "%s:%s" % (x['identifier_namespace_uri'], x['identifier_uid']), list(result))))



        return super(XMLImportView,self).get(request, *args, **kwargs)




class UploadFile(View):
    """
    Handles an uploaded file. Tries to detect the type according to the content and returns the appropriate object (e.g. file-observable)
    """

    def __identify_test_mechanism_file(self, file_content):
        # Try IOC
        try:
            xroot = etree.fromstring(file_content)
            # If the root looks like this, we are quite confident that this is a IOC file
            if xroot.tag.lower() == '{http://schemas.mandiant.com/2010/ioc}ioc':
                return 'ioc'
        except:
            pass

        # Try YARA
        reg = re.compile("^rule \w+$", re.IGNORECASE) # If a line starts with 'rule <some_name>', we think it's a yara file
        if reg.match(file_content):
            return 'yara'

        # Try SNORT
        reg = re.compile('^(alert|log|pass).*(->|<>|<-).*$', re.IGNORECASE)
        for l in file_content.splitlines():
            if reg.match(l):
                return 'snort'

        return None

    def __identify_observable_file(self, file_content):
        return None

    def identify_uploaded_file(self, file_content): 
        object_type = None
        
        # Test mechanisms type detection
        object_type = self.__identify_test_mechanism_file(file_content)
        if object_type is not None:
            return object_type
        
        # Observable type detection
        object_type = self.__identify_observable_file(file_content)
        if object_type is not None:
            return object_type

        return object_type


    def post(self, request, *args, **kwargs):
        res = {
            'status': False,
            'msg': 'An error occured.',
            'data': {}
        }
        FILES = request.FILES
        f = False
        if FILES.has_key(u'file'):
            f = FILES['file']
            file_content = f.read()

            ftype = self.identify_uploaded_file(file_content)
            ftype_ok = True
            # GUI passed allowed file types
            req_type = request.POST.get('dda_dropzone_type_allow', None)
            if req_type:
                req_type = req_type.split(',')
                if not (len(req_type)==1 and req_type[0]==''): # allowed not types empty
                    if not ftype in req_type: # if type not in specified types
                        ftype_ok = False
                        res['msg'] = 'The uploaded file could not be identified.'
                
            

            if ftype=='ioc' and ftype_ok:
                try:
                    xroot = etree.fromstring(file_content)
                    #xroot_string = etree.tostring(xroot, encoding='UTF-8', xml_declaration=False)

                    predef_id = xroot.get('id', None)
                    if predef_id:
                        predef_id = 'siemens_cert:Test_Mechanism-' + predef_id

                    res['status'] = True
                    res['msg'] = ''
                    res['data'] = [{ 'object_class': 'testmechanism',
                                     'object_type': 'Test_Mechanism',
                                     'object_subtype': 'IOC',
                                     'object_id': predef_id,
                                     'properties': { 'ioc_xml': b64encode(file_content),
                                                     'ioc_title': f.name,
                                                     'ioc_description': ''
                                                 }
                             }]
                except Exception as e:
                    res['msg'] =  str(e)
                    pass
            elif ftype=='snort' and ftype_ok:
                res['status'] = True
                res['msg'] = ''
                res['data'] = [{ 'object_class': 'testmechanism',
                                 'object_type': 'Test_Mechanism',
                                 'object_subtype': 'SNORT',
                                 'object_id': False,
                                 'properties': { 'snort_rules': b64encode(file_content),
                                                 'snort_title': f.name,
                                                 'snort_description': ''
                                             }
                             }]

            elif ftype_ok:
                res['status'] = True
                res['msg'] = ''


                md5 = hashlib.md5()
                md5.update(file_content)

                sha1 = hashlib.sha1()
                sha1.update(file_content)

                sha256 = hashlib.sha256()
                sha256.update(file_content)

                res['data'] = [{ 'object_class': 'observable',
                                 'object_type': 'File',
                                 'object_subtype': 'Default',
                                 'properties': { 'file_name': f.name,
                                                 'file_path': '',
                                                 'file_size': f.size,
                                                 'md5': md5.hexdigest(),
                                                 'sha1': sha1.hexdigest(),
                                                 'sha256': sha256.hexdigest()
                                             }
                             }]


        if not request.META.has_key('HTTP_X_REQUESTED_WITH'): # Indicates fallback (form based upload)
            ret  = '<script>'
            ret += 'var r = ' + json.dumps(res) + ';';
            ret += 'window.top._handle_file_upload_response(r);'
            ret += '</script>'
            return HttpResponse(ret)
        else: #fancy upload
            return HttpResponse(json.dumps(res), content_type="application/json")
