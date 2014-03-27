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

from dingos import DINGOS_INTERNAL_IOBJECT_FAMILY_NAME, DINGOS_TEMPLATE_FAMILY
from dingos.view_classes import BasicListView, BasicTemplateView

from dingos.importer import Generic_XML_Import

from models import GroupNamespaceMap

from django.views.generic import View
from transformer import stixTransformer

from .models import AuthoredData, GroupNamespaceMap

import libxml2

from . import DINGOS_AUTHORING_IMPORTER_REGISTRY

#from libmantis import *
#from mantis_client import utils

from forms import XMLImportForm

import forms as observables
from operator import itemgetter


logger = logging.getLogger(__name__)

def index(request):

    observableForms = []
    indicatorForms = []
    campaignForms = []
    threatActorForms = []
    for obj_elem in dir(observables):
        if obj_elem.startswith("Cybox"):
            _cls = getattr(observables, obj_elem)
            observableForms.append(_cls())
        elif obj_elem.startswith("StixIndicator"):
            _cls = getattr(observables, obj_elem)
            indicatorForms.append(_cls())
        elif obj_elem.startswith("StixCampaign"):
            _cls = getattr(observables, obj_elem)
            campaignForms.append(_cls())
        elif obj_elem.startswith("StixThreatActor"):
            _cls = getattr(observables, obj_elem)
            threatActorForms.append(_cls())
            


    relations = [
        {'label': 'Created', 'value': 'Created', 'description': 'Specifies that this object created the related object.'},
        {'label': 'Deleted', 'value': 'Deleted', 'description': 'Specifies that this object deleted the related object.'},
        {'label': 'Read_From', 'value': 'Read_From', 'description': 'Specifies that this object was read from the related object.'},
        {'label': 'Wrote_To', 'value': 'Wrote_To', 'description': 'Specifies that this object wrote to the related object.'},
        {'label': 'Downloaded_From', 'value': 'Downloaded_From', 'description': 'Specifies that this object was downloaded from the related object.'},
        {'label': 'Downloaded', 'value': 'Downloaded', 'description': 'Specifies that this object downloaded the related object.'},
        {'label': 'Uploaded', 'value': 'Uploaded', 'description': 'Specifies that this object uploaded the related object.'},
        {'label': 'Received_Via_Upload', 'value': 'Received_Via_Upload', 'description': 'Specifies that this object received the related object via upload.'},
        {'label': 'Opened', 'value': 'Opened', 'description': 'Specifies that this object opened the related object.'},
        {'label': 'Closed', 'value': 'Closed', 'description': 'Specifies that this object closed the related object.'},
        {'label': 'Copied', 'value': 'Copied', 'description': 'Specifies that this object copied the related object.'},
        {'label': 'Moved', 'value': 'Moved', 'description': 'Specifies that this object moved the related object.'},
        {'label': 'Sent', 'value': 'Sent', 'description': 'Specifies that this object sent the related object.'},
        {'label': 'Received', 'value': 'Received', 'description': 'Specifies that this object received the related object.'},
        {'label': 'Renamed', 'value': 'Renamed', 'description': 'Specifies that this object renamed the related object.'},
        {'label': 'Resolved_To', 'value': 'Resolved_To', 'description': 'Specifies that this object was resolved to the related object.'},
        {'label': 'Related_To', 'value': 'Related_To', 'description': 'Specifies that this object is related to the related object.'},
        {'label': 'Dropped', 'value': 'Dropped', 'description': 'Specifies that this object dropped the related object.'},
        {'label': 'Contains', 'value': 'Contains', 'description': 'Specifies that this object contains the related object.'},
        {'label': 'Extracted_From', 'value': 'Extracted_From', 'description': 'Specifies that this object was extracted from the related object.'},
        {'label': 'Installed', 'value': 'Installed', 'description': 'Specifies that this object installed the related object.'},
        {'label': 'Connected_To', 'value': 'Connected_To', 'description': 'Specifies that this object connected to the related object.'},
        {'label': 'FQDN_Of', 'value': 'FQDN_Of', 'description': 'Specifies that this object is an FQDN of the related object.'},
        {'label': 'Characterizes', 'value': 'Characterizes', 'description': 'Specifies that this object describes the properties of the related object. This is most applicable in cases where the related object is an Artifact Object and this object is a non-Artifact Object.'},
        {'label': 'Used', 'value': 'Used', 'description': 'Specifies that this object used the related object.'},
        {'label': 'Redirects_To', 'value': 'Redirects_To', 'description': 'Specifies that this object redirects to the related object.'}
    ]

    return render_to_response('dingos_authoring/%s/index.html' % DINGOS_TEMPLATE_FAMILY,{
        'title': 'Mantis Authoring',
        'observableForms': observableForms,
        'indicatorForms': indicatorForms,
        'campaignForms': campaignForms,
        'threatActorForms': threatActorForms,
        'relations': sorted(relations, key=itemgetter('label'))
    })

    



class transform(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        res = {}
        if True: #try:
            POST = request.POST
            jsn = ''
            if POST.has_key(u'jsn'):
                jsn = POST[u'jsn']
                submit_name = POST[u'submit_name']

                namespace_infos = list(GroupNamespaceMap.objects.filter(group__in=self.request.user.groups.all())[:1])

                if namespace_infos == []:
                    raise Exception("User not allowed to author data.")
                else:
                    namespace_uri = namespace_infos[0].default_namespace.uri
                    namespace_slug = namespace_infos[0].default_namespace.name
                    if not namespace_slug:
                        namespace_slug = 'dingos_author'




                AuthoredData.object_update_or_create(current_kind=AuthoredData.AUTHORING_JSON,
                                                     current_user=self.request.user,
                                                     current_name= submit_name,
                                                     current_timestamp='latest',
                                                     status=AuthoredData.DRAFT,
                                                     processor='test',
                                                     display_view='test',
                                                     data = jsn)

                t = stixTransformer(jsn=jsn,namespace_uri=namespace_uri,namespace_slug=namespace_slug)
                stix = t.getStix()

                if not stix:
                    return HttpResponse('{}', content_type="application/json")

                res['xml'] = stix
        #except Exception, e:
        #    res['error_msg'] = "An error occured: %s" % e.message
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
        for x in context['object_list']:
            #print dir(x)
            print 
            pass

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
            ns_def = root.nsDefs()
            while ns_def:
                ns_mapping[ns_def.name] = ns_def.content
                ns_def = ns_def.next

            try:
                ns_slug = root.ns().name
            except:
                ns_slug = None

            if ns_slug:
                namespace = ns_mapping.get(ns_slug,None)
            else:
                namespace = None

            importer_class = Generic_XML_Import
            for (matcher,mapped_importer_class) in DINGOS_AUTHORING_IMPORTER_REGISTRY:
                m = matcher.search(namespace)
                if m:
                    importer_class = mapped_importer_class
                    break
            importer = importer_class()
            result = importer.xml_import(xml_content = data['xml'])


            messages.success(self.request,"Submitted %s" % (namespace))

        return super(BasicTemplateView,self).get(request, *args, **kwargs)


