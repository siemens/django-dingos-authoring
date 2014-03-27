import json, collections
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from dingos.models import InfoObject
from django.db.models import Q

from braces.views import LoginRequiredMixin

from dingos import DINGOS_INTERNAL_IOBJECT_FAMILY_NAME
from dingos.view_classes import BasicListView
from django.views.generic import View
from transformer import stixTransformer

from dingos_authoring.models import AuthoredData

from libmantis import *
from mantis_client import utils

import forms as observables
from operator import itemgetter




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

    return render_to_response('dingos_authoring/index.html',{
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
        POST = request.POST
        jsn = ''
        if POST.has_key(u'j'):
            jsn = POST[u'j']


            AuthoredData.object_update_or_create(current_kind=AuthoredData.AUTHORING_JSON,
                                                 current_user=self.request.user,
                                                 current_name='1111',
                                                 status=AuthoredData.DRAFT,
                                                 processor='test',
                                                 display_view='test',
                                                 data = jsn)

        t = stixTransformer(jsn)
        stix = t.getStix()

        if not stix:
            return HttpResponse('{}', content_type="application/json")

        res['xml'] = stix
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



