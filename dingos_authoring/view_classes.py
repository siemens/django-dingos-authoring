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


from .models import GroupNamespaceMap

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
            return {'default_ns_uri': namespace_uri,
                    'default_ns_slug': namespace_slug,
                    'allowed_ns_uris': allowed_namespace_uris}
        else:
            raise NotImplementedError("Functionality for several authoring groups not yet implemented")
