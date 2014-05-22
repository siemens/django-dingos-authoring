from __future__ import absolute_import

from celery import shared_task


@shared_task(ignore_result=False)
def add(x, y):
    return x + y

@shared_task(ignore_result=False)
def scheduled_import(importer,xml):
    return importer.xml_import(xml_content = xml,
                               track_created_objects=True)
