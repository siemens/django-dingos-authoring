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

import json

from dingos.view_classes import BasicView

from .models import AuthoredData, GroupNamespaceMap

from django.http import HttpResponse, HttpResponseRedirect

class AuthoringMethodMixin(object):
    """
    We use this Mixin to enrich view with methods that are required
    by several authoring views.
    """
    def get_authoring_namespaces(self,force_single_group=True):

        namespace_infos = GroupNamespaceMap.get_authoring_namespace_info(self.request.user)

        if len(namespace_infos.keys()) == 0:
            raise StandardError("User not allowed to author data.")
        elif len(namespace_infos.keys()) > 1 and force_single_group:
            raise StandardError("Current user is member of more than one authoring groups")
        elif force_single_group:
            namespace_info = namespace_infos.values()[0]
            default_namespace = namespace_info['default']


            namespace_uri = default_namespace.uri
            namespace_slug = default_namespace.name
            if not namespace_slug:
                namespace_slug = 'dingos_author'

            allowed_namespace_uris = map(lambda x: x.uri, namespace_info['allowed'])
            return {'authoring_group': namespace_info['authoring_group'],
                    'default_ns_uri': namespace_uri,
                    'default_ns_slug': namespace_slug,
                    'allowed_ns_uris': allowed_namespace_uris}
        else:
            raise NotImplementedError("Functionality for several authoring groups not yet implemented")

class BasicProcessingView(AuthoringMethodMixin,BasicView):

    importer_class = None
    author_view = None
    transformer = None

    def post(self, request, *args, **kwargs):
        res = {}
        msg = ''
        if True: #try:
            POST = request.POST
            jsn = ''
            if POST.has_key(u'jsn'):
                jsn = POST[u'jsn']
                submit_name = POST[u'submit_name']
                submit_action = POST.get(u'action','generate')
                print submit_action
                try:
                    namespace_info = self.get_authoring_namespaces()
                except StandardError, e:
                    return HttpResponse(json.dumps({'msg':e.message}), content_type="application/json")



                AuthoredData.object_update_or_create(current_kind=AuthoredData.AUTHORING_JSON,
                                                     current_user=self.request.user,
                                                     current_group=namespace_info['authoring_group'],
                                                     current_name= submit_name,
                                                     current_timestamp='latest',
                                                     status=AuthoredData.DRAFT,
                                                     author_view=self.author_view,
                                                     data = jsn)

                if submit_action == 'save':
                    msg += "Draft saved.\n"

                elif submit_action in ["generate", "import"]:
                    t = self.transformer(jsn=jsn,
                                         namespace_uri=namespace_info['default_ns_uri'],
                                         namespace_slug=namespace_info['default_ns_slug'],)
                    stix = t.getStix()



                    if not stix:
                        msg += "STIX could not be created \n"
                        res['xml'] = ""
                    else:
                        res['xml'] = stix

                    if submit_action == 'import':

                        self.importer_class.xml_import

                        importer = self.importer_class(allowed_identifier_ns_uris=namespace_info['allowed_ns_uris'],
                                                            default_identifier_ns_uri=namespace_info['default_ns_uri'],
                                                            substitute_unallowed_namespaces=True)



                        result = importer.xml_import(xml_content = res['xml'],track_created_objects=True)

                        msg += ("Result %s" % result)

                        #except Exception, e:
            #    res['msg'] = "An error occured: %s" % e.message
        #    logger.error("Authoring attempt resulted in error %s, traceback %s" % (e.message,traceback.format_exc()))
        #    raise e

        if msg:
            res['msg'] = msg
        return HttpResponse(json.dumps(res), content_type="application/json")
