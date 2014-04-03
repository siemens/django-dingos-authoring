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



class XMLImportForm(forms.Form):
    xml = forms.CharField(required=False,
                            widget=widgets.Textarea(attrs={'cols':100,'rows':10,'style': 'height:auto; width:auto;'}),
                            validators=[validate_xml])

