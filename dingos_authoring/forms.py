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

from django.forms import widgets
from validators import validate_xml



class XMLImportForm(forms.Form):
    name = forms.CharField(required=False,
                           help_text="Name is displayed in list of imported XML; the name is not used in the import.",
                           max_length=256,
                           widget=widgets.TextInput(attrs={'size':'100','class':'vTextField'}))
    xml = forms.CharField(required=False,
                          help_text = """ATTENTION: Make sure that the identifier namespaces occuring in the XML
                                         are contained in your allowed namespaces (see display on right-hand side)!!! Otherwise, the created objects will be moved
                                         into a temporary namespace!!!""",
                          widget=widgets.Textarea(attrs={'cols':100,'rows':10,'style': 'height:auto; width:100%;resize:vertical;min-height:150px;'}),
                          validators=[validate_xml])


class GUIJSONImportForm(forms.Form):
    name = forms.CharField(required=True,
                           help_text="This name is shown as report name in authoring interface",
                           max_length=256,
                           widget=widgets.TextInput(attrs={'size':'100','class':'vTextField'}))
    json = forms.CharField(required=False,
                          help_text = """Paste here valid Mantis GUI JSON""",
                          widget=widgets.Textarea(attrs={'cols':100,'rows':10,'style': 'height:auto; width:100%;resize:vertical;min-height:150px;'}),
                          )



class SwitchAuthoringGroupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if 'group_choices' in kwargs:
            group_choices = kwargs['group_choices'] + [('','---')]
            del(kwargs['group_choices'])
        else:
            group_choices = []
        if 'initial_group' in kwargs:
            initial_group = kwargs['initial_group']
            del(kwargs['initial_group'])
        else:
            initial_group = 'blah'


        super(SwitchAuthoringGroupForm, self).__init__(*args, **kwargs)

        self.fields['group'] = forms.ChoiceField(choices=group_choices,
                                                 required=False
                                                 )
