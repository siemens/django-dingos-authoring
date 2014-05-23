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


from django import template
from django.utils.html import strip_tags
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from dingos.models import BlobStorage

from dingos import DINGOS_TEMPLATE_FAMILY

from dingos_authoring.view_classes import AuthoringMethodMixin


register = template.Library()



@register.inclusion_tag('dingos_authoring/%s/includes/_AuthoringNamespacesDisplay.html'% DINGOS_TEMPLATE_FAMILY,takes_context=True)
def show_AuthoringNamespaces(context):
    namespace_info = AuthoringMethodMixin.get_authoring_namespaces(context['view'].request.user,
                                                                   force_single_group=True,
                                                                       fail_silently=True)

    current_group = None
    allowed_uris = None
    namespace_uri = None

    if namespace_info:
        current_group=namespace_info['authoring_group']
        namespace_uri=namespace_info['default_ns_uri']
        allowed_uris = set(namespace_info['allowed_ns_uris'])
        allowed_uris.add(namespace_uri)
        allowed_uris = sorted(list(allowed_uris))

    result =  {'current_group':current_group,
               'allowed_ns_uris' : allowed_uris,
               'default_ns_uri' : namespace_uri}


    return result

