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


import logging
import pprint
from django.utils import timezone

from django.db import models

from django.contrib.auth.models import User, Group

from dingos.models import IdentifierNameSpace, InfoObject

logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=2)

class Processor(models.Model):
    name = models.CharField(max_length=255,
                            help_text="""Either transformer or importer""",
                            unique=True
    )

    def __unicode__(self):
        return self.name


class DisplayView(models.Model):
    name = models.CharField(max_length=255,
                            help_text="""View Identifier""",
                            unique=True
    )

    def __unicode__(self):
        return self.name

class DataName(models.Model):
    name = models.CharField(max_length=255,
                            help_text="""Name/Identifier""",
                            unique=True
    )

    def __unicode__(self):
        return self.name


class GroupNamespaceMap(models.Model):
    """

    """

    group = models.OneToOneField(Group,unique=True)

    default_namespace = models.ForeignKey(IdentifierNameSpace, related_name='authoring_default_for')

    allowed_namespaces = models.ManyToManyField(IdentifierNameSpace, related_name='authoring_allowed_for',blank=True)

    def __unicode__(self):
        return "%s: %s" % (self.group,self.default_namespace.uri)

class AuthoredData(models.Model):
    """

    """

    AUTHORING_JSON = 0
    XML = 1

    DATA_KIND = ((AUTHORING_JSON, "JSON (Dingos Authoring)"),
                     (XML, "XML"),
    )

    kind = models.SmallIntegerField(choices=DATA_KIND,
                                    default=AUTHORING_JSON,
                                    help_text="""Type of data""")

    DRAFT = 0
    IMPORTED = 1
    TEMPLATE = 2

    STATUS = ((DRAFT,"Draft"),
              (IMPORTED,"Imported"),
              (TEMPLATE,"Template"))


    status = models.SmallIntegerField(choices=STATUS,
                                    default=DRAFT,
                                    help_text="""Status""")

    processor = models.ForeignKey("Processor")

    display_view = models.ForeignKey("DisplayView",
                                     blank=True)

    name = models.ForeignKey(DataName)

    data = models.TextField(blank=True)

    user = models.ForeignKey(User)

    timestamp = models.DateTimeField()


    class Meta:
        unique_together = ("user",
                           "name",
                           "kind",
                           "timestamp")


    @staticmethod
    def object_create(kind=None,
                      status=None,
                      processor=None,
                      display_view='',
                      data=None,
                      user=None,
                      name=None,
                      timestamp=timezone.now()):

        if isinstance(name,basestring):
            name_obj, created = DataName.objects.get_or_create(name=name)
        else:
            name_obj = name

        if isinstance(processor,basestring):
            processor_obj, created = Processor.objects.get_or_create(name=processor)
        else:
            processor_obj = processor

        if isinstance(display_view,basestring):
            display_view_obj, created = DisplayView.objects.get_or_create(name=display_view)
        else:
            display_view_obj = display_view

        return AuthoredData.objects.create(kind=kind,
                                           user=user,
                                           name=name_obj,
                                           status=status,
                                           processor=processor_obj,
                                           display_view=display_view_obj,
                                           data=data,
                                           timestamp=timestamp)


    @staticmethod
    def object_update(current_kind,
                      current_user,
                      current_name,
                      current_timestamp,
                      **kwargs
                      ):

        print "Args %s %s %s %s %s" % (current_kind,current_user,current_name,current_timestamp,kwargs)

        if isinstance(current_name,basestring):
            current_name_obj, created = DataName.objects.get_or_create(name=current_name)


        if 'name' in kwargs:
            name_value = kwargs['name']
            if isinstance(name_value,basestring):
                name_obj, created = DataName.objects.get_or_create(name=name_value)
                kwargs['name'] = name_obj

        if 'processor' in kwargs:
            processor_value = kwargs['processor']
            if isinstance(processor_value,basestring):
                processor_obj, created = Processor.objects.get_or_create(name=processor_value)
                kwargs['processor'] = processor_obj

        if 'display_view' in kwargs:
            display_view_value = kwargs['display_view']
            if isinstance(display_view_value,basestring):
                display_view_obj, created = DisplayView.objects.get_or_create(name=display_view_value)
                kwargs['display_view'] = display_view_obj



        print "All %s" % AuthoredData.objects.all()

        objs = AuthoredData.objects.filter(kind=current_kind,
                                           user=current_user,
                                           name=current_name_obj)
        print "Existing %s" % objs
        if current_timestamp == 'latest':
            objs = list(objs.order_by('-timestamp')[:1])
            print "Found %s" % objs
            if len(objs) == 1:
                # Below is an ugly hack, but in the limited application here it works.
                objs[0].__dict__.update(kwargs)
                objs[0].save()
                return 1
            else:
                return 0

        elif isinstance(current_timestamp,timezone):
            objs.filter(timestamp=current_timestamp)
        elif current_timestamp == 'all':
            pass
        else:
            raise TypeError("Timestamp must be a timezone value, 'lastest', or 'all'.")

        timestamp=current_timestamp

        return objs.update(**kwargs)

    @staticmethod
    def object_update_or_create(current_kind,
                                current_user,
                                current_name,
                                current_timestamp,
                                **kwargs):

        if current_timestamp == 'all':
            raise TypeError("This method cannot be called with timestamp = 'all'.")

        updated_objs = AuthoredData.object_update(current_kind,
                                                  current_user,
                                                  current_name,
                                                  current_timestamp,
                                                  **kwargs)
        if updated_objs == 0:
            # no object was found, so we create one.

            if not 'name' in kwargs:
                kwargs['name'] = current_name
            if not 'kind' in kwargs:
                kwargs['kind'] = current_kind
            if not 'user' in kwargs:
                kwargs['user'] = current_user
            if not 'timestamp' in kwargs:
                if current_timestamp == 'latest':
                    kwargs['timestamp'] = timezone.now()
                else:
                    kwargs['timestamp'] = current_timestamp

            AuthoredData.object_create(**kwargs)


class InfoObject2AuthoredData(models.Model):
    iobject = models.OneToOneField(InfoObject,related_name = 'created_from_thru')
    authored_data = models.OneToOneField(AuthoredData)


