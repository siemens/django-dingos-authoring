from __future__ import absolute_import

from celery import shared_task

from dingos.models import InfoObject

from dingos_authoring.models import AuthoredData


import logging

import traceback

logger = logging.getLogger(__name__)


@shared_task(ignore_result=False)
def add(x, y):
    return x + y

@shared_task(ignore_result=False)
def scheduled_import(importer,
                     xml,
                     xml_import_obj):

    created_object_info = importer.xml_import(xml_content = xml,
                                              track_created_objects=True)

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
        top_level_iobject = InfoObject.objects.get(pk=created_object_ids[-1])
    except:
        top_level_iobject = None

    if top_level_iobject:
        # We need to retrieve the object once more, because
        # if we save now, we are going to overwrite the object
        # that has been written directly after the scheduled
        # import was called.
        # The 'add' call above, on the other hand, was ok,
        # because that does not change the object -- it creates
        # objects in an internal through-model

        xml_import_obj_reloaded = AuthoredData.objects.get(pk=xml_import_obj.pk)

        xml_import_obj_reloaded.top_level_iobject = top_level_iobject

        xml_import_obj_reloaded.save()

    return created_object_info
