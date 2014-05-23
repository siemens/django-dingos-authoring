from __future__ import absolute_import

from celery import shared_task

from dingos.models import InfoObject

@shared_task(ignore_result=False)
def add(x, y):
    return x + y

@shared_task(ignore_result=False)
def scheduled_import(importer,xml):
    created_object_info = importer.xml_import(xml_content = xml,
                                          track_created_objects=True)

    # Now call set_name on each object once more;
    # this is required, because object names may depend on
    # names of referenced objects, and they do not always
    # get created in the proper order.

    created_object_ids = [x['pk'] for x in created_object_info if x['existed']==False]

    created_objects = InfoObject.objects.filter(pk__in=created_object_ids)

    for object in created_objects:
        name = object.set_name()

    return created_object_info
