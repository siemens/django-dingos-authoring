# Copyright (c) Siemens AG, 2013
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



from django import forms
from django.templatetags.static import static

from django.forms import widgets
from validators import validate_xml

"""
Classes describe front-end element. Element properties then show up in the resulting JSON as properties. 
Properties with a leading 'I_' will not be converted to JSON
"""

class StixThreatActor(forms.Form):
    CONFIDENCE_TYPES = (
        ('high', 'High'),
        ('med', 'Medium'),
        ('low', 'Low')
    )
    object_type = forms.CharField(initial="ThreatActor", widget=forms.HiddenInput)
    I_object_display_name = forms.CharField(initial="Threat Actor", widget=forms.HiddenInput)
    I_icon =  forms.CharField(initial=static('img/stix/threat_actor.svg'), widget=forms.HiddenInput)
    identity_name = forms.CharField(max_length=1024, help_text="Required if Campaign/ThreatActor should be generated")
    identity_aliases = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Line by line aliases of this threat actor'}), required=False, )
    title = forms.CharField(max_length=1024)
    description = forms.CharField(widget=forms.Textarea, required=False)
    confidence = forms.ChoiceField(choices=CONFIDENCE_TYPES, required=False, initial="med")
    information_source = forms.CharField(max_length=1024)


class StixCampaign(forms.Form):
    STATUS_TYPES = (
        ('Success', 'Success'),
        ('Fail', 'Fail'),
        ('Error', 'Error'),
        ('Complete/Finish', 'Complete/Finish'),
        ('Pending', 'Pending'),
        ('Ongoing', 'Ongoing'),
        ('Unknown', 'Unknown')
    )
    CONFIDENCE_TYPES = (
        ('high', 'High'),
        ('med', 'Medium'),
        ('low', 'Low')
    )
    HANDLING_TYPES = (
        ('white', 'White'),
        ('green', 'Green'),
        ('amber', 'Amber'),
        ('red', 'Red')
    )
    object_type = forms.CharField(initial="Campaign", widget=forms.HiddenInput)
    I_object_display_name = forms.CharField(initial="Campaign", widget=forms.HiddenInput)
    I_icon =  forms.CharField(initial=static('img/stix/campaign.svg'), widget=forms.HiddenInput)
    name = forms.CharField(max_length=1024, help_text="Required if Campaign/ThreatActor should be generated")
    title = forms.CharField(max_length=1024)
    description = forms.CharField(widget=forms.Textarea, required=False)
    status = forms.ChoiceField(choices=STATUS_TYPES, required=False, initial="Unknown")
    activity_timestamp_from = forms.CharField(max_length=1024)
    activity_timestamp_to = forms.CharField(max_length=1024)
    confidence = forms.ChoiceField(choices=CONFIDENCE_TYPES, required=False, initial="med")
    handling = forms.ChoiceField(choices=HANDLING_TYPES, required=False, initial="amber")
    information_source = forms.CharField(max_length=1024)


class StixIndicator(forms.Form):
    CONFIDENCE_TYPES = (
        ('high', 'High'),
        ('med', 'Medium'),
        ('low', 'Low')
    )
    object_type = forms.CharField(initial="Indicator", widget=forms.HiddenInput)
    I_object_display_name = forms.CharField(initial="Indicator", widget=forms.HiddenInput)
    I_icon =  forms.CharField(initial=static('img/stix/indicator.svg'), widget=forms.HiddenInput)
    indicator_producer = forms.CharField(max_length=1024)
    indicator_title = forms.CharField(max_length=1024)
    indicator_description = forms.CharField(widget=forms.Textarea, required=False)
    indicator_confidence = forms.ChoiceField(choices=CONFIDENCE_TYPES, required=False, initial="med")


class CyboxEmailObjectForm(forms.Form):
    object_type = forms.CharField(initial="EmailMessage", widget=forms.HiddenInput)
    I_object_display_name = forms.CharField(initial="Email Message", widget=forms.HiddenInput)
    I_icon =  forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)
    from_ = forms.CharField(max_length=256, required=False)
    to = forms.CharField(widget=forms.Textarea(attrs={'placeholder':"Recipients line by line"}), required=False)
    subject = forms.CharField(max_length=1024) # required to identify observable later in list
    in_reply_to = forms.CharField(max_length=1024, required=False)
    received_date = forms.CharField(required=False)
    raw_header = forms.CharField(widget=forms.Textarea, required=False)
    raw_body = forms.CharField(widget=forms.Textarea, required=False)
    links = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Links line by line'}), required=False)


class CyboxFileObjectForm(forms.Form):
    object_type = forms.CharField(initial="File", widget=forms.HiddenInput)
    I_object_display_name = forms.CharField(initial="File", widget=forms.HiddenInput)
    I_icon =  forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)
    file_name = forms.CharField(required=False)
    file_path = forms.CharField(required=False)
    file_size = forms.IntegerField(required=False)
    md5 = forms.CharField(max_length=32) # required to identify observable later in list
    sha1 = forms.CharField(max_length=40, required=False)
    sha256 = forms.CharField(max_length=64, required=False)


class CyboxDNSRecordObjectForm(forms.Form):
    object_type = forms.CharField(initial="DNSRecord", widget=forms.HiddenInput)
    I_object_display_name = forms.CharField(initial="DNS Record", widget=forms.HiddenInput)
    I_icon =  forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)
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
    object_type = forms.CharField(initial="Address", widget=forms.HiddenInput)
    I_object_display_name = forms.CharField(initial="Address", widget=forms.HiddenInput)
    I_icon =  forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)
    observable_id = forms.CharField(initial="", widget=forms.HiddenInput)
    ip_addr = forms.CharField(max_length=45)
    category = forms.ChoiceField(choices=CATEGORY_TYPES, required=False, initial="ipv4-addr")
    is_source = forms.BooleanField(initial=False)
    is_destination = forms.BooleanField(initial=False)
    condition = forms.ChoiceField(choices=CONDITIONS_TYPES, required=False, initial="Equals")


class CyboxC2OjbectForm(forms.Form):
    object_type = forms.CharField(initial="C2Object", widget=forms.HiddenInput)
    I_object_display_name = forms.CharField(initial="Command & Control Domains/IPs", widget=forms.HiddenInput)
    I_icon =  forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)
    _multi = forms.CharField(initial=static('true'), widget=forms.HiddenInput)
    data = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Copy & Paste your Command and Control Domains/IPs here line by line.'}), required=False)


class CyboxArtifactObjectForm(forms.Form):
    ARTIFACT_TYPES = (
        ('TYPE_FILE', 'File'),
        ('TYPE_MEMORY', 'Memory Region'),
        ('TYPE_FILE_SYSTEM', 'File System Fragment'),
        ('TYPE_NETWORK', 'Network Traffic'),
        ('TYPE_GENERIC', 'Generic Data Region')
    )
    object_type = forms.CharField(initial="Artifact", widget=forms.HiddenInput)
    I_object_display_name = forms.CharField(initial="Artifact", widget=forms.HiddenInput)
    I_icon =  forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)
    artifact_type = forms.ChoiceField(choices=ARTIFACT_TYPES, required=False, initial="TYPE_GENERIC")
    data = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Paste your artifact here.'}), required=False)


class CyboxPortOjbectForm(forms.Form):
    object_type = forms.CharField(initial="Port", widget=forms.HiddenInput)
    I_object_display_name = forms.CharField(initial="Port", widget=forms.HiddenInput)
    I_icon =  forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)
    port_value = forms.CharField(max_length=5, required=True)
    layer4_protocol = forms.CharField(max_length=1024, required=False)


class CyboxHTTPSessionObjectForm(forms.Form):
    object_type = forms.CharField(initial="HTTPSession", widget=forms.HiddenInput)
    I_object_display_name = forms.CharField(initial="HTTP Session", widget=forms.HiddenInput)
    I_icon =  forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)
    method = forms.CharField(max_length=1024, required=False)
    uri = forms.CharField(max_length=1024, required=False)
    host = forms.CharField(max_length=1024, required=False)
    port = forms.CharField(max_length=5, required=False)
    user_agent = forms.CharField(max_length=1024, required=False)


class CyboxURIOjbectForm(forms.Form):
    URI_TYPES = (
        ('TYPE_URL', 'URL'),
        ('TYPE_GENERAL', 'General URN'),
        ('TYPE_DOMAIN', 'Domain Name')
    )
    object_type = forms.CharField(initial="URI", widget=forms.HiddenInput)
    I_object_display_name = forms.CharField(initial="Generic URI", widget=forms.HiddenInput)
    I_icon =  forms.CharField(initial=static('img/stix/observable.svg'), widget=forms.HiddenInput)
    type_ = forms.ChoiceField(choices=URI_TYPES, required=False, initial="TYPE_URL")
    value = forms.CharField(max_length=2048, required=False)




class XMLImportForm(forms.Form):
    xml = forms.CharField(required=False,
                            widget=widgets.Textarea(attrs={'cols':100,'rows':10,'style': 'height:auto; width:auto;'}),
                            validators=[validate_xml])

