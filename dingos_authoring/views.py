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
from mantis_client.mantis_templates import alpaca_test as mantis_indicators


def index(request):

    json_skeleton = """
{
    "title": "",
    "description": "",
    "type": "object",
    "properties": {

    },
    "definitions": {
        "indicator_title": {
            "type": "string",
            "title": "Indicator Title",
            "description": "Provide a descriptive title of the indicator",
            "required": true
        },
        "indicator_description": {
            "type": "string",
            "title": "Indicator Description",
            "required": false
        },
        "indicator_alternative": {
            "type": "string",
            "title": "Indicator Alternative ID",
            "description": "e.g. INVES-XXXXX",
            "required": false
        },
        "indicator_type": {
            "title": "Indicator Type",
            "enum": ["IP Watchlist"]
        },
	"indicator_confidence": {
            "title": "Indicator Confidence",
	    "enum": ["High","Medium","Low"],    
            "required": true,
            "default": "Medium"
	},
        "indicator_sighting": {
            "title": "Indicator Sighting",
            "enum": ["PLM-CERT","DSIE","Mandiant"],
            "required": true,
            "default":"PLM-CERT"
        }
    }
}
    """

    options_skeleton = """
{
    "fields": {
    },
    "definitions": {
    	"indicator_sighting": {
            "type": "select"
	},
    	"indicator_type": {
            "type": "select"
	}
    }
}
    """

    options_skeleton = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(options_skeleton)
    options_skeleton = json.dumps(options_skeleton)

    available_templates = {};
    for obj_elem in (dir(mantis_indicators)):
        if obj_elem.startswith("TEMPLATE_"):
            _cls = getattr(mantis_indicators, obj_elem)
            available_templates[obj_elem]= _cls()

    def get_available_templates():
        ret = []
        for atn, ati in available_templates.iteritems():
            if 'FORMDEF' in dir(ati):
                samp = ati.FORMDEF
                jsamp = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(samp)

                # Prepare/enrich json template

                temp = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(json_skeleton)
                temp['title'] = jsamp['meta']['title']
                temp['description'] = jsamp['meta']['description']
                temp['properties'] = jsamp['data']

                tempo = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(options_skeleton)
                tempo['fields'] = jsamp['options']

                ret.append({'id': atn.replace('TEMPLATE_', ''),
                            'title': temp['title'],
                            'template': json.dumps(temp),
                            'options': json.dumps(tempo)
                        })
        return ret

    def get_template_json(id):
        at = get_available_templates()
        for t in at:
            if t['id']==id:
                return t['template']
        return '{}'

    def get_options_json(id):
        at = get_available_templates()
        for t in at:
            if t['id']==id:
                return t['options']
        return '{}'

    def get_template(id):
        at = get_available_templates()
        for t in at:
            if t['id']==id:
                return t
        return None


    at = get_available_templates()
    selected_template = at[0]['id'] if at else None
    try:
        selected_template = request.GET['template']
    except (KeyError):
        pass



    # from schema import alpaca_generator
    # sc = alpaca_generator(get_template_json(selected_template))
    # schema_template = sc.get_schema()
    # options_template = sc.get_options()
    schema_template = get_template_json(selected_template)
    options_template = get_options_json(selected_template)

    print schema_template
    print options_template

    res = {
        'title': 'MANTIS Dingos Authoring',
        'available_templates': at,
        'selected_template': get_template(selected_template),
        'schema': schema_template,
        'options': options_template
    }
    return render_to_response('dingos_authoring/index.html',
                              res,
                              context_instance=RequestContext(request))
    



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
