import json, collections
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from libmantis import *
from mantis_client import utils
from mantis_client.mantis_templates import indicators as mantis_indicators


def index(request):

    available_templates = {};
    for obj_elem in (dir(mantis_indicators)):
        if obj_elem.startswith("TEMPLATE_"):
            _cls = getattr(mantis_indicators, obj_elem)
            available_templates[obj_elem]= _cls()

    def get_available_templates():
        ret = []
        for atn, ati in available_templates.iteritems():
            samp = ati.SAMPLE_JSON
            #jsamp = json.loads(samp)
            jsamp = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(samp)
            ret.append({'id': atn.replace('TEMPLATE_', ''),
                        'title': jsamp['data']['title'],
                        'template': json.dumps(jsamp['data'])})
        return ret

    def get_template_json(id):
        at = get_available_templates()
        for t in at:
            if t['id']==id:
                return t['template']
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

    #TOOD: Add custom template (click and drop)


    res = {
        'title': 'MANTIS Dingos Authoring',
        'available_templates': at,
        'selected_template': get_template(selected_template),
        'json_template': get_template_json(selected_template)
    }
    return render_to_response('dingos_authoring/index.html',
                              res,
                              context_instance=RequestContext(request))


# Ajax autocomplete view
def ref(request):
    res = {'success':False}
    if request.method == u'GET':
        GET = request.GET
        if GET.has_key(u'type') and GET.has_key(u'q'):
            q = GET[u'q']
            t = GET[u'type']
            print "TODO: fetch data for type", t, "and with q", q
            #TODO: fetch data from db and prepare result set
            res['result'] = [
                {'title': 'Test Item 1', 'value': 'testitem1'},
                {'title': 'Test Item 2', 'value': 'testitem2'},
                {'title': 'Test Item 3', 'value': 'testitem3'},
            ]
            res['success'] = True
    res = json.dumps(res)
    return HttpResponse(res, content_type='application/json')

