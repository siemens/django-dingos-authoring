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

from dingos.models import InfoObject, InfoObject2Fact
from django.db.models import Q
from django.utils import timezone

from django.contrib import messages

from django.contrib.auth.models import User, Group
from mantis_authoring.utilities import name_cybox_obj, find_similar_cybox_obj


from braces.views import LoginRequiredMixin, SuperuserRequiredMixin

from dingos.core.utilities import lookup_in_re_list
from dingos import DINGOS_INTERNAL_IOBJECT_FAMILY_NAME, DINGOS_TEMPLATE_FAMILY
from dingos.view_classes import BasicListView, BasicTemplateView, BasicJSONView, BasicFilterView

from dingos.importer import Generic_XML_Import
from querystring_parser import parser


from models import GroupNamespaceMap

from django.views.generic import View

from .models import AuthoredData, GroupNamespaceMap

from .view_classes import AuthoringMethodMixin

import libxml2
from lxml import etree
from base64 import b64encode

from . import DINGOS_AUTHORING_IMPORTER_REGISTRY

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



class GetAuthoringObjectReference(BasicJSONView):
    """
    View serving a reference to an existing object
    """
    @property
    def returned_obj(self):
        res = {
            'status': False,
            'msg': 'An error occured',
            'data': list(InfoObject.objects.none())
        }

        POST = self.request.POST
        post_dict = parser.parse(POST.urlencode())

        object_element = post_dict.get('el', {})
        object_type = object_element.get('object_type', None).lower().strip()
        object_subtype = object_element.get('object_subtype', 'Default')
        queryterm = post_dict.get('q', '')

        if not object_element or not object_type or object_type == '':
            pass
        elif object_type == 'campaign':
            q_q = Q(name__icontains=queryterm) & Q(iobject_type__name__icontains="Campaign")
            data =  InfoObject.objects.all(). \
                    exclude(latest_of=None). \
                    exclude(iobject_family__name__exact=DINGOS_INTERNAL_IOBJECT_FAMILY_NAME). \
                    exclude(iobject_family__name__exact='ioc'). \
                    filter(q_q). \
                    distinct().order_by('name')[:10]
            # TODO: fetch campaigns and associated threatactor from DB
            res['data'] = map(lambda x : {'id': x.identifier.uid, 'name': x.name, 'cat': str(x.iobject_type), 'threatactor': {}}, data)
        
            
        elif object_type == 'threatactor':
            q_q = Q(name__icontains=queryterm) & Q(iobject_type__name__icontains="ThreatActor")
            data =  InfoObject.objects.all(). \
                    exclude(latest_of=None). \
                    exclude(iobject_family__name__exact=DINGOS_INTERNAL_IOBJECT_FAMILY_NAME). \
                    exclude(iobject_family__name__exact='ioc'). \
                    filter(q_q). \
                    distinct().order_by('name')[:10]
            res['data'] = map(lambda x : {'id': x.identifier.uid, 'name': x.name, 'cat': str(x.iobject_type)}, data)

        else:
            try:
                im = importlib.import_module('mantis_authoring.cybox_object_transformers.' + object_type)
                template_obj = getattr(im,'TEMPLATE_%s' % object_subtype)()
                data = template_obj.autocomplete(queryterm, object_element)
                res['data'] = map(lambda x : {'id': x.iobject.identifier.uid, 'name': x.iobject.name, 'cat': str(x.iobject.iobject_type)}, data)
                res['status'] = True
                res['msg'] = ''
            except Exception as e:
                res['msg'] = str(e)
                
        return res



class GetAuthoringSimilarObjects(BasicJSONView):
    """
    View serving a list of similar objects
    """
    @property
    def returned_obj(self):
        res = {
            'status': False,
            'msg': 'An error occured',
            'data': {
                'items': []
            }
        }

        POST = self.request.POST
        post_dict = parser.parse(POST.urlencode())

        object_element = post_dict.get('observable_properties', {})
        object_type = object_element.get('object_type', '').lower().strip()
        object_subtype = object_element.get('object_subtype', 'Default')

        try:
            im = importlib.import_module('mantis_authoring.cybox_object_transformers.' + object_type)
            template_obj = getattr(im,'TEMPLATE_%s' % object_subtype)()
            cybox_xml = template_obj.process_form(object_element).to_xml()
            fact_term_list = template_obj.get_relevant_fact_term_list()
            similar_objects = find_similar_cybox_obj(cybox_xml, fact_term_list)
            for similar_obj in similar_objects:
                sobj = similar_obj.facts.all()
                sobj = sobj.filter(fact_term__term__in=fact_term_list)

                det = []
                for fact in sobj:
                    det.append(
                        ', '.join(map(lambda x: x.get('value') ,fact.fact_values.values()))
                    )


                res['data']['items'].append({
                    'title': similar_obj.name,
                    'details': ', '.join(det)
                })
            res['status'] = True
            if(len(res['data']['items'])==0):
                res['status'] = False
                res['msg'] = 'Sorry, we could not find similar objects!'

        except Exception as e:
            raise e
            res['msg'] = str(e)
        
        return res



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


        if not request.is_ajax(): # Indicates fallback (form based upload)
            ret  = '<script>'
            ret += 'var r = ' + json.dumps(res) + ';';
            ret += 'window.top._handle_file_upload_response(r);'
            ret += '</script>'
            return HttpResponse(ret)
        else: #fancy upload
            return HttpResponse(json.dumps(res), content_type="application/json")



class GetAuthoringNamespace(BasicJSONView, AuthoringMethodMixin):
    """
    View serving the namespace of the currently logged in user
    """
    @property
    def returned_obj(self):
        res = {
            'status': False,
            'msg': 'An error occured fetching your namespace information',
            'data': None
        }

        if self.request.user:
            try:
                ns = self.get_authoring_namespaces(self.request.user)
                del ns['authoring_group']
                res['status'] = True
                res['msg'] = ''
                res['data'] = ns
            except StandardError as e:
                res['msg'] = str(e)
            finally:
                pass

        return res



# class ValidateObject(BasicJSONView, AuthoringMethodMixin):
#     """
#     Validates an object passed from the GUI. 
#     """
#     @property
#     def returned_obj(self):
#         res = {
#             'status': False,
#             'msg': 'An error occured validating the object.',
#             'data': None
#         }

#         POST = self.request.POST
#         post_dict = parser.parse(POST.urlencode())

#         observable_properties = post_dict.get('observable_properties', {})
#         object_type = observable_properties.get('object_type', None)
#         object_subtype = observable_properties.get('object_subtype', 'Default')

#         try:
#             im = importlib.import_module('mantis_authoring.cybox_object_transformers.' + object_type.lower())
#             template_obj = getattr(im,'TEMPLATE_%s' % object_subtype)()
#             obs_form_valid = template_obj.validate_form(observable_properties)

            


#         except Exception as e:
#             print e

#         return res


from django.views.generic.edit import FormView
class ValidateObject(FormView):

    def errors_to_json(self, errors):
        """
        Convert a Form error list to JSON::
        """
        return dict(
                (k, map(unicode, v))
                for (k,v) in errors.iteritems()
            )

    def get_form_kwargs(self, data=None):
        kwargs = super(ValidateObject, self).get_form_kwargs()
        if data:
            kwargs.update({'initial': data, 'data': data})
        return kwargs

    def post(self, request, *args, **kwargs):

        POST = self.request.POST
        post_dict = parser.parse(POST.urlencode())
        observable_properties = post_dict.get('observable_properties', {})
        observable_properties['observable_id'] = post_dict.get('observable_id')
        observable_properties['I_object_display_name'] = 'NONE'
        observable_properties['I_icon'] = 'NONE'
        object_type = observable_properties.get('object_type', None)
        object_subtype = observable_properties.get('object_subtype', 'Default')

        try:
            im = importlib.import_module('mantis_authoring.cybox_object_transformers.' + object_type.lower())
            template_obj = getattr(im,'TEMPLATE_%s' % object_subtype)()

            form_class = template_obj.ObjectForm
            form = form_class(**self.get_form_kwargs(observable_properties))
        except:
            res = {
                'status': False,
                'msg': 'An error occured validating the object.',
                'data': None
            }
            return HttpResponse(json.dumps(res), content_type='application/json', )

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, *args, **kwargs):
        res = {
            'status': True,
            'msg': 'Validation successful',
            'data': None
        }
        return HttpResponse(json.dumps(res), content_type='application/json', )

    def form_invalid(self, form, *args, **kwargs):
        res = {
            'status': True,
            'msg': 'An error occured validating the object.',
            'data': self.errors_to_json(form.errors)
        }
        return HttpResponse(json.dumps(res), content_type='application/json', )
