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


from __future__ import absolute_import

from celery import shared_task

from dingos import DINGOS_EXPORT_VIEW_TOP_LEVEL_TYPES_THAT_TRIGGER_TRANSFER

from dingos.models import InfoObject

from dingos.forms import check_tag_validity

from dingos_authoring.models import AuthoredData

from dingos_authoring import DINGOS_AUTHORING_POSTPROCESSOR_TASK

import logging

import importlib

import traceback

logger = logging.getLogger(__name__)


@shared_task(ignore_result=False)
def add(x, y):
    return x + y

@shared_task(ignore_result=False)
def scheduled_import(importer,
                     xml,
                     xml_import_obj,
                     import_jsn=None,
                     user=None):

    import_result = importer.xml_import(xml_content = xml,
                                        track_created_objects=True)

    created_object_info = import_result.get('created_object_info',[])

    # Now call set_name on each object once more;
    # this is required, because object names may depend on
    # names of referenced objects, and they do not always
    # get created in the proper order.

    created_object_ids = [x['pk'] for x in created_object_info]

    created_objects = list(InfoObject.objects.filter(pk__in=created_object_ids))

    for object in created_objects:
        name = object.set_name()

    xml_import_obj.yielded_iobjects.add(*created_objects)

    try:
        top_level_iobjects = InfoObject.objects.\
            filter(pk__in=created_object_ids).\
            filter(iobject_type__name__in=DINGOS_EXPORT_VIEW_TOP_LEVEL_TYPES_THAT_TRIGGER_TRANSFER)
    except:
        top_level_iobjects = []



    if len(top_level_iobjects) == 1:
        # We need to retrieve the object once more, because
        # if we save now, we are going to overwrite the object
        # that has been written directly after the scheduled
        # import was called.
        # The 'add' call above, on the other hand, was ok,
        # because that does not change the object -- it creates
        # objects in an internal through-model

        top_level_iobject = top_level_iobjects[0]

        xml_import_obj_reloaded = AuthoredData.objects.get(pk=xml_import_obj.pk)

        xml_import_obj_reloaded.top_level_iobject = top_level_iobject

        xml_import_obj_reloaded.save()

        # Now we run the import into the actionables backend

    for top_level_iobject in top_level_iobjects:

        mod_name, func_name = DINGOS_AUTHORING_POSTPROCESSOR_TASK.rsplit('.',1)
        mod = importlib.import_module(mod_name)
        postprocessor_task = getattr(mod,func_name)

        postprocessor_task.delay(top_level_iobject,
                                 import_jsn,
                                 user)

        #"stix_header_report_type": "incident_report",
        #"stix_header_title": "IR-12385134",
        #"stix_header_rtnr": "Siemens-CERT#444444"

    return created_object_info

