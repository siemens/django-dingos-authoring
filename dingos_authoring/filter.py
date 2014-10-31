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


import django_filters

from .models import AuthoredData

from dingos.filter import ExtendedDateRangeFilter, create_order_keyword_list

class ImportFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_type='icontains',
                                     label='Name contains')

    kind = django_filters.ChoiceFilter(choices=list(AuthoredData.DATA_KIND) + [('','Any kind')],required=False)

    timestamp = ExtendedDateRangeFilter(label="Import Timestamp")

    class Meta:
        order_by = create_order_keyword_list(['timestamp','name','kind'])
        model = AuthoredData
        fields = ['timestamp','name','kind']

class AuthoringObjectFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_type='icontains',
                                     label='Name contains')

    timestamp = ExtendedDateRangeFilter(label="Import Timestamp")


    status = django_filters.ChoiceFilter(choices=list(AuthoredData.STATUS_WO_AUTOSAVE) + [('','Any status')],required=False)

    class Meta:
        order_by = create_order_keyword_list(['user','timestamp','name','status'])
        model = AuthoredData
        fields = ['timestamp','name','status','user']






