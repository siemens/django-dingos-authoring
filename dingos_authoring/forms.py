from django import forms
from django.templatetags.static import static

class StixIndicator(forms.Form):
    CONFIDENCE_TYPES = (
        ('high', 'High'),
        ('med', 'Medium'),
        ('low', 'Low')
    )
    indicator_type = forms.CharField(initial="Indicator", widget=forms.HiddenInput)
    indicator_producer = forms.CharField(max_length=1024)
    indicator_title = forms.CharField(max_length=1024)
    indicator_description = forms.CharField(widget=forms.Textarea, required=False)
    indicator_confidence = forms.ChoiceField(choices=CONFIDENCE_TYPES, required=False, initial="med")
    icon = forms.CharField(initial=static('img/stix/indicator.svg'), widget=forms.HiddenInput)

class CyboxEmailObjectForm(forms.Form):
    object_type = forms.CharField(initial="EmailMessage", widget=forms.HiddenInput)
    from_ = forms.CharField(max_length=256, required=False)
    to = forms.CharField(widget=forms.Textarea, help_text="one recipient per line", required=False)
    subject = forms.CharField(max_length=1024) # required to identify observable later in list
    in_reply_to = forms.CharField(max_length=1024, required=False)
    received_date = forms.CharField(required=False)
    raw_header = forms.CharField(widget=forms.Textarea, required=False)
    raw_body = forms.CharField(widget=forms.Textarea, required=False)
    links = forms.CharField(widget=forms.Textarea, help_text="one link per line", required=False)
    icon = forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)

class CyboxFileObjectForm(forms.Form):
    object_type = forms.CharField(initial="File", widget=forms.HiddenInput)
    file_name = forms.CharField(required=False)
    file_path = forms.CharField(required=False)
    #file_extension = forms.CharField(max_length=256, required=False)
    file_size = forms.IntegerField(required=False)
    md5 = forms.CharField(max_length=32) # required to identify observable later in list
    sha1 = forms.CharField(max_length=40, required=False)
    sha256 = forms.CharField(max_length=64, required=False)
    icon = forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)

class CyboxDNSRecordObjectForm(forms.Form):
    object_type = forms.CharField(initial="DNSRecord", widget=forms.HiddenInput)
    domain_name = forms.CharField(max_length=1024) # required to identify observable later in list
    ip_address = forms.CharField(max_length=15, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    icon = forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)

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
    observable_id = forms.CharField(initial="", widget=forms.HiddenInput)
    object_type = forms.CharField(initial="Address", widget=forms.HiddenInput)
    ip_addr = forms.CharField(max_length=45)
    category = forms.ChoiceField(choices=CATEGORY_TYPES, required=False, initial="ipv4-addr")
    is_source = forms.BooleanField(initial=False)
    is_destination = forms.BooleanField(initial=False)
    condition = forms.ChoiceField(choices=CONDITIONS_TYPES, required=False, initial="Equals")
    icon = forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)



class CyboxC2OjbectForm(forms.Form):
    object_type = forms.CharField(initial="C2Object", widget=forms.HiddenInput)
    data = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Copy & Paste your C2 Domains/IPs here line by line.'}), required=False)
    icon = forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)


class CyboxArtifactObjectForm(forms.Form):
    ARTIFACT_TYPES = (
        ('TYPE_FILE', 'File'),
        ('TYPE_MEMORY', 'Memory Region'),
        ('TYPE_FILE_SYSTEM', 'File System Fragment'),
        ('TYPE_NETWORK', 'Network Traffic'),
        ('TYPE_GENERIC', 'Generic Data Region')
    )
    object_type = forms.CharField(initial="Artifact", widget=forms.HiddenInput)
    artifact_type = forms.ChoiceField(choices=ARTIFACT_TYPES, required=False, initial="TYPE_GENERIC")
    data = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Paste your artifact here.'}), required=False)
    icon = forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)


class CyboxPortOjbectForm(forms.Form):
    object_type = forms.CharField(initial="Port", widget=forms.HiddenInput)
    port_value = forms.CharField(max_length=5, required=True)
    layer4_protocol = forms.CharField(max_length=1024, required=False)
    icon = forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)


class CyboxHTTPSessionObjectForm(forms.Form):
    object_type = forms.CharField(initial="HTTPSession", widget=forms.HiddenInput)
    method = forms.CharField(max_length=1024, required=False)
    uri = forms.CharField(max_length=1024, required=False)
    host = forms.CharField(max_length=1024, required=False)
    port = forms.CharField(max_length=5, required=False)
    referrer = forms.CharField(max_length=1024, required=False)
    content_length = forms.CharField(max_length=1024, required=False)
    content_type = forms.CharField(max_length=1024, required=False)
    user_agent = forms.CharField(max_length=1024, required=False)
    icon = forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)


class CyboxURIOjbectForm(forms.Form):
    URI_TYPES = (
        ('TYPE_URL', 'URL'),
        ('TYPE_GENERAL', 'General URN'),
        ('TYPE_DOMAIN', 'Domain Name')
    )
    object_type = forms.CharField(initial="URI", widget=forms.HiddenInput)
    type_ = forms.ChoiceField(choices=URI_TYPES, required=False, initial="TYPE_URL")
    value = forms.CharField(max_length=2048, required=False)
    icon = forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)
