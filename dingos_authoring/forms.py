from django import forms

import time

class CyboxEmailObjectForm(forms.Form):
    object_id = forms.CharField(initial="", widget=forms.HiddenInput)
    object_type = forms.CharField(initial="EmailMessage", widget=forms.HiddenInput)
    from_ = forms.CharField(max_length=256, required=False)
    to = forms.CharField(widget=forms.Textarea, help_text="one recipient per line", required=False)
    subject = forms.CharField(max_length=1024) # required to identify observable later in list
    in_reply_to = forms.CharField(max_length=1024, required=False)
    received_date = forms.CharField(required=False)
    raw_header = forms.CharField(widget=forms.Textarea, required=False)
    raw_body = forms.CharField(widget=forms.Textarea, required=False)
    links = forms.CharField(widget=forms.Textarea, help_text="one link per line", required=False)

class CyboxFileObjectForm(forms.Form):
    object_id = forms.CharField(initial="", widget=forms.HiddenInput)
    object_type = forms.CharField(initial="File", widget=forms.HiddenInput)
    file_name = forms.CharField(required=False)
    file_extension = forms.CharField(max_length=256, required=False)
    file_size = forms.IntegerField(required=False)
    md5 = forms.CharField(max_length=32) # required to identify observable later in list
    sha1 = forms.CharField(max_length=40, required=False)
    sha256 = forms.CharField(max_length=64, required=False)

class CyboxDNSRecordObjectForm(forms.Form):
    object_id = forms.CharField(initial="", widget=forms.HiddenInput)
    object_type = forms.CharField(initial="DNSRecord", widget=forms.HiddenInput)
    domain_name = forms.CharField(max_length=1024) # required to identify observable later in list
    ip_address = forms.CharField(max_length=15, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

class CyboxAddressObjectForm(forms.Form):
    CATEGORY_TYPES = (
        ('ipv4-addr', 'IPv4 Address'),
        ('ipv4-net', 'IPv4 Network'),
        ('ipv6-addr', 'IPv6 Address'),
        ('ipv6-net', 'IPv6 Network')
    )
    CONDITIONS_TYPES = (
        ('InclusiveBetween', 'Inclusive Between'),
        ('StartsWith', 'Starts With'),
        ('Contains', 'Contains'),
        ('Equals', 'Equals')
    )
    object_id = forms.CharField(initial="", widget=forms.HiddenInput)
    object_type = forms.CharField(initial="Address", widget=forms.HiddenInput)
    ip_addr = forms.CharField(max_length=45)
    category = forms.ChoiceField(choices=CATEGORY_TYPES, required=False, initial="ipv4-addr")
    is_source = forms.BooleanField(initial=False)
    is_destination = forms.BooleanField(initial=False)
    condition = forms.ChoiceField(choices=CONDITIONS_TYPES, required=False, initial="Equals")


class StixIndicator(forms.Form):
    CONFIDENCE_TYPES = (
        ('high', 'High'),
        ('med', 'Medium'),
        ('low', 'Low')
    )
    indicator_producer = forms.CharField(max_length=1024)
    indicator_title = forms.CharField(max_length=1024)
    indicator_description = forms.CharField(widget=forms.Textarea, required=False)
    indicator_type = forms.CharField(max_length=1024, required=False, initial="")
    indicator_confidence = forms.ChoiceField(choices=CONFIDENCE_TYPES, required=False, initial="med")
    indicator_id = forms.CharField(initial="Indicator", widget=forms.HiddenInput)

