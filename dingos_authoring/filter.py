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






