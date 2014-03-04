import json, collections
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from dingos.models import InfoObject
from django.db.models import Q
from dingos import DINGOS_INTERNAL_IOBJECT_FAMILY_NAME
from dingos.view_classes import BasicListView

from libmantis import *
from mantis_client import utils
from mantis_client.mantis_templates import indicators as mantis_indicators

import forms as observables


def index(request):

    observableForms = []
    indicatorForms = []
    for obj_elem in dir(observables):
        if obj_elem.startswith("Cybox"):
            _cls = getattr(observables, obj_elem)
            observableForms.append(_cls())
        elif obj_elem.startswith("Stix"):
            _cls = getattr(observables, obj_elem)
            indicatorForms.append(_cls())

    return render_to_response('dingos_authoring/index.html',{
        'observableForms': observableForms,
        'indicatorForms': indicatorForms
    })
    



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
