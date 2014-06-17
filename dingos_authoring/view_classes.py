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

import json, logging, traceback

from dingos.view_classes import BasicView
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

from .models import AuthoredData, GroupNamespaceMap, UserAuthoringInfo

from . import DINGOS_AUTHORING_CELERY_BUG_WORKAROUND

from . import tasks

# Ordinarily, the celery tasks used here should be imported like so::
#    from .tasks import add, scheduled_import
# There is however, at least one installation, where this does not work:
# the task returned via this import does not have set the
# right results backend.
# So we prune the required tasks from the app object defined in mantis.celery
# until the issue is resolved


                                

logger = logging.getLogger(__name__)

class AuthoringMethodMixin(object):
    """
    We use this Mixin to enrich view with methods that are required
    by several authoring views.
    """

    @staticmethod
    def get_authoring_namespaces(user,fail_silently=True):
        # Is there a default authoring namespace for this user?
        try:
            user_authoring_info = UserAuthoringInfo.objects.get(user=user)
            namespace_info = user_authoring_info.default_authoring_namespace_info

        except ObjectDoesNotExist:

            # No default exists. Let's see whether the user is associated
            # with any authoring group

            namespace_infos = GroupNamespaceMap.get_authoring_namespace_info(user)


            if len(namespace_infos.keys()) == 0:
                # No authoring for this user; fail silently or complain
                if fail_silently:
                    return None
                else:
                    raise StandardError("User not allowed to author data.")
            elif len(namespace_infos.keys()) > 1 :
                # more than one group, but no default has been defined
                # (see above). Therefore: silently fail or complain.
                if fail_silently:
                    return namespace_infos.items()
                else:
                    raise StandardError("Current user is member of more than one authoring groups")

            else:
                # There must be exactly one associated authoring group for this user
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


    # To make sure that a view does not have to call get_authoring_namespaces more than once,
    # we store the result of the namespace lookup in the following variable:

    _namespace_info = False

    @property
    def namespace_info(self):
        """
        Lookup authoring namespace information for the user;
        the result (either ``None``, the retrieved information
        for a single or the default authoring group, or a list
        of results for several authoring groups)

        is stored in ``self._namespace_info``.
        """
        if self._namespace_info != False:
            return self._namespace_info
        else:
            self._namespace_info = self.get_authoring_namespaces(self.request.user,fail_silently=True)
            return self._namespace_info




class BasicProcessingView(AuthoringMethodMixin,BasicView):
    importer_class = None
    author_view = None
    transformer = None

    def post(self, request, *args, **kwargs):
        res = {
            'status': False,
            'msg': 'An error occured.'
        }

        try:
            POST = request.POST
            res['msg']=''
            jsn = ''
            if POST.has_key(u'jsn'):
                jsn = POST[u'jsn']
                submit_name = POST[u'submit_name']
                identifier = POST.get(u'id')
                submit_action = POST.get(u'action')
                if not (identifier or submit_action):
                    res['msg'] = 'Something went wrong (ajax request missed id and/or action'
                    res['status'] = False
                    return HttpResponse(json.dumps(res), content_type="application/json")

                namespace_info = self.namespace_info
                if not namespace_info:
                    res['msg'] = 'You are not member of an Authoring Group'
                    res['status'] = False
                    return HttpResponse(json.dumps(res), content_type="application/json")
                elif isinstance(namespace_info,list):
                    res['msg'] = 'You are member of several authoring groups but you have not selected a' \
                                 ' default authoring group.'
                    res['status'] = False
                    return HttpResponse(json.dumps(res), content_type="application/json")

                if submit_action in ['save','release','import']:

                    try:
                        previous_obj = AuthoredData.objects.get(identifier__name=identifier,
                                                                group = namespace_info['authoring_group'],
                                                                latest = True)
                        status = previous_obj.status
                        if status == AuthoredData.IMPORTED:
                            status = AuthoredData.UPDATE
                    except ObjectDoesNotExist:
                        previous_obj = None
                        status = AuthoredData.DRAFT

                    if previous_obj and previous_obj.user != self.request.user:
                        res['msg'] = 'The authoring object has been taken from you by user %s; you are not allowed' \
                                     ' to save the object anymore.' % previous_obj.user

                        res['status'] = False
                        return HttpResponse(json.dumps(res), content_type="application/json")

                    if previous_obj and previous_obj.data == jsn:
                        res['msg'] = "No changes to be saved. "
                    else:
                        obj = AuthoredData.object_create(kind=AuthoredData.AUTHORING_JSON,
                                                   user=self.request.user,
                                                   group=namespace_info['authoring_group'],
                                                   identifier= identifier,
                                                   timestamp=timezone.now(),
                                                   status=status,
                                                   name=submit_name,
                                                   author_view=self.author_view,
                                                   data = jsn)

                        res['msg'] = 'Changes saved. '

                    if submit_action == 'release':
                        obj = AuthoredData.object_create(kind=AuthoredData.AUTHORING_JSON,
                                                   user=None,
                                                   group=namespace_info['authoring_group'],
                                                   identifier= identifier,
                                                   timestamp=timezone.now(),
                                                   status=status,
                                                   name=submit_name,
                                                   author_view=self.author_view,
                                                   data = jsn)
                        res['msg'] += 'Report released. '

                    res['status'] = True

                if submit_action in ["generate", "import"]:
                    t = self.transformer(jsn=jsn,
                                         namespace_uri=namespace_info['default_ns_uri'],
                                         namespace_slug=namespace_info['default_ns_slug'],)
                    stix = t.getStix()

                    if not stix:
                        res['msg'] += "STIX could not be created."
                        res['status'] = False
                        return HttpResponse(json.dumps(res), content_type="application/json")
                    else:
                        res['status'] = True
                        res['msg'] += "STIX successfully generated. "
                        res['xml'] = stix

                    if submit_action == 'import':
                        self.importer_class.xml_import

                        importer = self.importer_class(allowed_identifier_ns_uris=namespace_info['allowed_ns_uris'],
                                                            default_identifier_ns_uri=namespace_info['default_ns_uri'],
                                                            substitute_unallowed_namespaces=True)


                        xml_import_obj = AuthoredData.object_create(kind=AuthoredData.XML,
                                                                    user=request.user,
                                                                    group=namespace_info['authoring_group'],
                                                                    identifier= identifier,
                                                                    timestamp=timezone.now(),
                                                                    status=AuthoredData.IMPORTED,
                                                                    name=submit_name,
                                                                    author_view=None,
                                                                    data = res['xml'])


                        #result = scheduled_import.delay(importer=importer,

                        if DINGOS_AUTHORING_CELERY_BUG_WORKAROUND:
                            # This is an ugly hack which breaks the independence of the django-dingos-authoring
                            # app from the top-level configuration.
                            # The hack may be required in instances where the celery tasks defined in Django
                            # are not instantiated correctly: we have a system on which the configuration of
                            # celery as seen when starting the worker is perfectly ok, yet within Django,
                            # the tasks are not assigned the correct backend.
                            from mantis.celery import app as celery_app



                        result = tasks.scheduled_import.delay(importer=importer,
                                                        xml=res['xml'],
                                                        xml_import_obj=xml_import_obj)

                        xml_import_obj.processing_id = result.id

                        xml_import_obj.save()

                        AuthoredData.object_create(kind=AuthoredData.AUTHORING_JSON,
                                                   user=None,
                                                   group=namespace_info['authoring_group'],
                                                   identifier= identifier,
                                                   timestamp= timezone.now(),
                                                   status=AuthoredData.IMPORTED,
                                                   name=submit_name,
                                                   author_view=self.author_view,
                                                   data = jsn,
                                                   yielded = xml_import_obj)


                        res['status'] = True
                        res['msg'] += "Import started and report released. "

        except Exception, e:
            res['msg'] = "An error occured: %s" % str(e)
            logger.error("Authoring attempt resulted in error %s, traceback %s" % (str(e),traceback.format_exc()))
            res['status'] = False


        return HttpResponse(json.dumps(res), content_type="application/json")



