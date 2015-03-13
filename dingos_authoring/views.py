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

import sys, re, traceback, json, collections, logging, libxml2, importlib, pkgutil, hashlib
from uuid import uuid4
from base64 import b64encode
from operator import itemgetter


from . import tasks

from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone


from braces.views import LoginRequiredMixin, SuperuserRequiredMixin

from dingos import DINGOS_INTERNAL_IOBJECT_FAMILY_NAME, DINGOS_TEMPLATE_FAMILY
from dingos.core.utilities import lookup_in_re_list
from dingos.importer import Generic_XML_Import
from dingos.models import InfoObject, InfoObject2Fact
from dingos.view_classes import BasicListView, BasicTemplateView, BasicJSONView, BasicXMLView, BasicFilterView, BasicListActionView



from forms import XMLImportForm, SwitchAuthoringGroupForm
import forms as observables

from . import DINGOS_AUTHORING_IMPORTER_REGISTRY, DINGOS_AUTHORING_CELERY_BUG_WORKAROUND

from .filter import ImportFilter, AuthoringObjectFilter
from .models import GroupNamespaceMap, AuthoredData, Identifier, UserAuthoringInfo
from .view_classes import AuthoringMethodMixin




logger = logging.getLogger(__name__)

AUTHORING_IMPORTER_REGISTRY = []

for (matcher,module,class_name) in DINGOS_AUTHORING_IMPORTER_REGISTRY:
    my_module = importlib.import_module(module)
    AUTHORING_IMPORTER_REGISTRY.append((matcher,getattr(my_module,class_name)))



#if DINGOS_AUTHORING_CELERY_BUG_WORKAROUND:
#    # This is an ugly hack which breaks the independence of the django-dingos-authoring
#    # app from the top-level configuration.
#    # The hack may be required in instances where the celery tasks defined in Django
#    # are not instantiated correctly: we have a system on which the configuration of
#    # celery as seen when starting the worker is perfectly ok, yet within Django,
#    # the tasks are not assigned the correct backend.
#    from mantis.celery import app as celery_app
#    print celery_app
#
#    #tasks = celery_app.tasks#
#
#    #add = celery_app.tasks['dingos_authoring.tasks.add']
#    #scheduled_import = celery_app.tasks['dingos_authoring.tasks.scheduled_import']
#else:
#    pass
#    #from .tasks import add,scheduled_import
#    #fake_tasks = {'dingos_authoring.tasks.add':add,
#    #         'dingos_authoring.tasks.scheduled_import':scheduled_import
#    #        }
#
#    #celery_app = FakeCeleryApp(tasks=fake_tasks)

class AuthoredDataHistoryView(AuthoringMethodMixin,BasicListView):
    """
    Overview of history of an Authoring object.
    """

    template_name = 'dingos_authoring/%s/AuthoredDataHistory.html' % DINGOS_TEMPLATE_FAMILY

    counting_paginator = True

    @property
    def title(self):
        latest_auth_obj = AuthoredData.objects.get(group=self.namespace_info['authoring_group'],
                                                      identifier__name=self.kwargs['id'],
                                                      latest=True)
        return "History of '%s' " % latest_auth_obj.name

    @property
    def queryset(self):
        namespace_info = self.namespace_info

        if not namespace_info:
            messages.error(self.request,"You are not member of an authoring group.")
            return AuthoredData.objects.exclude(id__contains='')
        if isinstance(namespace_info,list):
            messages.error(self.request,"You are member of several authoring groups but have not selected a"
                                        " default group.")

            return AuthoredData.objects.exclude(id__contains='')


        return AuthoredData.objects.filter(group=self.namespace_info['authoring_group'],
                                                  identifier__name=self.kwargs['id']).order_by('-timestamp'). \
            prefetch_related('identifier','group','user','author_view').prefetch_related('top_level_iobject',
                                                                                         'top_level_iobject__identifier',
                                                                                         'top_level_iobject__identifier__namespace')

    def get_context_data(self, **kwargs):
        context = super(AuthoredDataHistoryView, self).get_context_data(**kwargs)
        context['highlight_pk'] = self.request.GET.get('highlight',None)
        return context




class index(AuthoringMethodMixin,BasicFilterView):
    """
    Overview of saved drafts.
    """

    counting_paginator = True

    @property
    def title(self):
        if self.namespace_info:
            if isinstance(self.namespace_info,list):
                return "No drafts or imports to be shown (no active authoring group selected)"
            else:
                return "Drafts and Imports of Authoring Group %s" % self.namespace_info['authoring_group']
        else:
            return "No drafts or imports to be shown (user not member of an authoring group)"

    template_name = 'dingos_authoring/%s/AuthoredObjectList.html' % DINGOS_TEMPLATE_FAMILY
    filterset_class = AuthoringObjectFilter


    @property
    def queryset(self):

        namespace_info = self.namespace_info

        if not namespace_info:
            messages.error(self.request,'You are not member of an Authoring Group.')
            return AuthoredData.objects.exclude(pk__gt=-1)

        elif isinstance(namespace_info,list):
            messages.error(self.request,'You are member of several authoring groups but you have not selected an' \
                                        ' active authoring group. Please do so in the "Switch Authoring Group" dialogue'
                                        ' available from the user menu (top right-hand corner).')
            return  AuthoredData.objects.exclude(pk__gt=-1)

        return AuthoredData.objects.filter(Q(kind=AuthoredData.AUTHORING_JSON,group=namespace_info['authoring_group'],latest=True)
                                       &
                                       (Q(status=AuthoredData.AUTOSAVE) | Q(status=AuthoredData.UPDATE) | Q(status=AuthoredData.DRAFT) | Q(status=AuthoredData.IMPORTED))). \
        prefetch_related('identifier','group','user','author_view').prefetch_related('top_level_iobject',
                                                                                     'top_level_iobject__identifier',
                                                                                     'top_level_iobject__identifier__namespace')


    list_actions = [('Take from owner', 'url.dingos_authoring.index.action.take', 0)]





class ImportsView(BasicFilterView):
    """
    Overview of saved drafts.
    """
    title = "Imports"
    template_name = 'dingos_authoring/%s/ImportList.html' % DINGOS_TEMPLATE_FAMILY


    filterset_class= ImportFilter

    title = 'Imports'


    @property
    def queryset(self):
        queryset = AuthoredData.objects.filter(
                                           user=self.request.user,
                                           status=AuthoredData.IMPORTED)

        return queryset






class GetDraftJSON(AuthoringMethodMixin,BasicJSONView):
    """
    View serving latest draft of given name, or respond with the list of available templates
    """
    @property
    def returned_obj(self):
        authoring_group = self.namespace_info['authoring_group']
        res = {
            'status': False,
            'msg': 'An error occured loading the requested template',
            'data': None
        }

        if 'list' in self.request.GET:
            json_obj_l = AuthoredData.objects.filter(
                kind = AuthoredData.AUTHORING_JSON,
                user = self.request.user,
                group = authoring_group,
                status = AuthoredData.DRAFT,
                latest = True
            ).prefetch_related('identifier','group','user','author_view').prefetch_related('top_level_iobject',
                                                                                           'top_level_iobject__identifier',
                                                                                           'top_level_iobject__identifier__namespace')


            res['status'] = True
            res['msg'] = ''
            res['data'] = []
            for el in json_obj_l:                
                res['data'].append({
                    'id': el.identifier.name, 
                    'name': el.name,
                    'date': el.timestamp.strftime("%Y-%m-%d %H:%M")
                })

        else:
            name = self.request.GET.get('name',False)
            try:
                json_obj = AuthoredData.objects.get(Q(kind=AuthoredData.AUTHORING_JSON,
                                                      group=authoring_group,
                                                      identifier__name=name,
                                                      latest=True,
                                                      )
                                                     & (Q(status=AuthoredData.DRAFT)
                                                        |Q(status=AuthoredData.UPDATE)
                                                        |Q(status=AuthoredData.IMPORTED))
                                                     &
                                                     (Q(user__isnull=True) | Q(user=self.request.user))

                                                      )
            except ObjectDoesNotExist:
                res['msg'] = 'Could not access object %s of group %s' %(name,authoring_group)
                res['status'] = False
                return res
            except MultipleObjectsReturned:
                res['msg'] = """Something is wrong in the database: there are several "latest" objects
                                of group %s with identifier %s""" % (authoring_group,name)
                return res




            if not json_obj.user:
                # The user needs to take the object in order to edit it -- this is
                # done automatically here.
                if json_obj.status == AuthoredData.IMPORTED:
                    status = AuthoredData.UPDATE
                else:
                    status = json_obj.status
                json_obj = AuthoredData.object_copy(json_obj,user=self.request.user,status=status)

            res['data'] = {}
            res['data']['jsn'] = json_obj.content # TODO
            res['data']['name'] = json_obj.name
            res['data']['id'] = json_obj.identifier.name
            res['status'] = True
            res['msg'] = 'Loaded \'' + json_obj.name + '\''

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
        self.form = XMLImportForm({'name':'Import of XML via GUI'})
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

            importer_class = None

            importer_class = lookup_in_re_list(AUTHORING_IMPORTER_REGISTRY,namespace)

            if not importer_class:
                messages.error(self.request,"Do not know how to import XML with namespace '%s'" % (namespace))
            else:
                importer = importer_class(allowed_identifier_ns_uris=namespace_info['allowed_ns_uris'] + [namespace_info['default_ns_uri']],
                                               default_identifier_ns_uri=namespace_info['default_ns_uri'],
                                               substitute_unallowed_namespaces=True)

                if False: # Celery switched off

                    result = importer.xml_import(xml_content = data['xml'],
                                                 track_created_objects=True)
                    messages.success(self.request,"Imported objects: %s" % ", ".join(map(lambda x: "%s:%s" % (x['identifier_namespace_uri'], x['identifier_uid']), list(result))))

                else:
                    identifier = Identifier.objects.create(name="%s" % uuid4())
                    authored_data = AuthoredData.objects_create(identifier = identifier,
                                                                name = data.get('name',"Import of XML via GUI"),
                                                                status = AuthoredData.IMPORTED,
                                                                kind = AuthoredData.XML,
                                                                data = data['xml'],
                                                                user = self.request.user,
                                                                group = namespace_info['authoring_group'],
                                                                timestamp = timezone.now(),
                                                                latest=True)


                    result = tasks.scheduled_import.delay(importer=importer,
                                                    xml=data['xml'],
                                                    xml_import_obj=authored_data)

                    authored_data.processing_id = result.id
                    authored_data.save()




                    messages.info(self.request,'Import started.')

                self.form = XMLImportForm()

        return super(XMLImportView,self).get(request, *args, **kwargs)





class TakeReportView(AuthoringMethodMixin,BasicListActionView):


    # The base query limits down the objects to the objects that
    # the user is actually allowed to act upon. This is to prevent
    # the user from fiddling with the data submitted by his browser
    # and inserting identifiers of objects that were not offered
    # by the view.


    template_name = 'dingos_authoring/%s/actions/TakeAuthoringDataObject.html' % DINGOS_TEMPLATE_FAMILY

    title = 'Take report(s) from owner'

    description = "When taking a report from another user, you become its owner and thus the only person" \
                  " allowed to edit the report. Make sure that you only take a report that is not currently" \
                  " edited by its current owner!"

    @property
    def action_model_query(self):
        base_query = AuthoredData.objects.filter(Q(kind=AuthoredData.AUTHORING_JSON,
                                                   group=self.namespace_info['authoring_group'],
                                                   latest=True) &
                                                 (Q(status=AuthoredData.DRAFT)
                                                  | Q(status=AuthoredData.UPDATE)
                                                  | Q(status=AuthoredData.IMPORTED)))
        return base_query




    def _take_authoring_data_obj(self,form_data,authoring_data_obj):
        if authoring_data_obj.user == self.request.user:
            return (None,"'%s' is already owned by you." % authoring_data_obj.name)
        elif authoring_data_obj.status in [AuthoredData.DRAFT,AuthoredData.UPDATE]:
            old_user = authoring_data_obj.user
            obj = AuthoredData.object_copy(authoring_data_obj, user= self.request.user)

            return (True, "'%s' is now owned by you instead of %s" % (obj.name, old_user))
        elif authoring_data_obj.status == AuthoredData.IMPORTED:
            obj= AuthoredData.object_copy(authoring_data_obj,
                                         user= self.request.user,
                                         status = AuthoredData.UPDATE)
            return (True, "'%s' has been put into DRAFT mode and is now owned by you." % obj.name)
        else:
            return (False, "Do not know how to treat '%s'" % authoring_data_obj.name)



    @property
    def action_list(self):
        return  [{'action_predicate': lambda x,y: True,
                  'action_function': lambda x,y: self._take_authoring_data_obj(x,y)}]









class GetAuthoringNamespace(AuthoringMethodMixin, BasicJSONView):
    """
    View serving the namespace of the currently logged in user
    """
    @property
    def returned_obj(self):
        res = {
            'status': False,
            'msg': 'An error occurred fetching your namespace information',
            'data': None
        }

        if self.request.user:
            try:
                ns = self.get_authoring_namespaces(self.request.user,fail_silently=False)
                del ns['authoring_group']
                res['status'] = True
                res['msg'] = ''
                res['data'] = ns
            except StandardError as e:
                res['msg'] = str(e)
            finally:
                pass

        return res



class CeleryTest(SuperuserRequiredMixin,BasicTemplateView):
    """
    View for editing the saved searches of a user.
    """

    template_name = 'dingos_authoring/%s/tests/CeleryTest.html' % DINGOS_TEMPLATE_FAMILY
    title = 'Test of Celery'

    def get_context_data(self, **kwargs):
        context = super(CeleryTest, self).get_context_data(**kwargs)
        #print celery_app.tasks
        #result = celery_app.tasks['dingos_authoring.tasks.add'].delay(2,2)



        if DINGOS_AUTHORING_CELERY_BUG_WORKAROUND:
            # This is an ugly hack which breaks the independence of the django-dingos-authoring
            # app from the top-level configuration.
            # The hack may be required in instances where the celery tasks defined in Django
            # are not instantiated correctly: we have a system on which the configuration of
            # celery as seen when starting the worker is perfectly ok, yet within Django,
            # the tasks are not assigned the correct backend.
            from mantis.celery import app as celery_app


        result = tasks.add.delay(2,2)

        status0 = result.status
        value1 = result.get(timeout=1)
        status1 = result.status

        context['status0'] = result.status
        context['value'] = result.get(timeout=1)
        context['status1'] = result.status
        return context



class SwitchAuthoringGroupView(AuthoringMethodMixin,BasicTemplateView):
    """
    View for editing the saved searches of a user.
    """

    template_name = 'dingos_authoring/%s/actions/SwitchAuthoringGroup.html' % DINGOS_TEMPLATE_FAMILY
    title = 'Switch Authoring Group'

    form = None

    def build_form(self,*args):
        ns_info = self.get_authoring_namespaces(self.request.user,return_available_groups=True)

        if not ns_info:
            # User has no authoring groups
            return None
        else:
            group_choices = []

            for (i,j) in ns_info['all_authoring_groups']:
                group_choices.append((i,i))


            if len(args) == 0:
                # No values have been set; we set the initial value here
                if 'authoring_group' in ns_info:
                    default = ns_info['authoring_group']
                else:
                    default = ''
                args = [{'group': default}]

            self.form = SwitchAuthoringGroupForm(*args,
                                                 group_choices=group_choices,
                                                 initial = {'group': ''})

    def get(self, request, *args, **kwargs):
        self.build_form()

        return super(SwitchAuthoringGroupView,self).get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        self.build_form(request.POST.dict())

        if self.form and self.form.is_valid():
            selected_group = self.form.cleaned_data['group']
            if selected_group:
                namespace_map = GroupNamespaceMap.objects.get(group__name=selected_group)

                try:
                    user_authoring_info = UserAuthoringInfo.objects.get(user=request.user)
                    user_authoring_info.default_authoring_namespace_info=namespace_map
                    user_authoring_info.save()
                except ObjectDoesNotExist:
                    UserAuthoringInfo.objects.create(user=request.user,
                                                     default_authoring_namespace_info=namespace_map)
                messages.success(request,"Authoring group switched.")
            else:
                messages.info(request,"Leaving settings unchanged.")

        return super(SwitchAuthoringGroupView,self).get(request, *args, **kwargs)


class ImportedXMLView(BasicXMLView):
    @property
    def returned_xml(self):
        iobject_id = self.kwargs.get('pk', None)
        iobject = InfoObject.objects.get(pk=iobject_id)
        authored_objects = iobject.yielded_by.all().filter(kind=AuthoredData.XML).order_by('-timestamp')

        if authored_objects:
            authored_object = authored_objects[0]
            return authored_object.content
