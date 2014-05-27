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

from .tasks import scheduled_import

import dingos_authoring.read_settings




logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=2)



class AuthorView(models.Model):
    name = models.CharField(max_length=255,
                            help_text="""View Identifier""",
                            unique=True
    )

    def __unicode__(self):
        return self.name

class Identifier(models.Model):
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

    @staticmethod
    def get_authoring_namespace_info(user):

        namespace_infos = GroupNamespaceMap.objects.filter(group__in=user.groups.all()).prefetch_related('default_namespace',
                                                                                                         'allowed_namespaces',
                                                                                                         'group')
        result = {}

        for namespace_info in namespace_infos:
            result[namespace_info.group.name] = {'authoring_group' : namespace_info.group,
                                                 'default':namespace_info.default_namespace,
                                                 'allowed':namespace_info.allowed_namespaces.all()}

        return result



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
    AUTOSAVE = 3


    STATUS_WO_AUTOSAVE = ((DRAFT,"Draft"),
                          (IMPORTED,"Imported"),
                          (TEMPLATE,"Template"))

    STATUS = tuple(list(STATUS_WO_AUTOSAVE) + [(AUTOSAVE,"Autsave")])

    status = models.SmallIntegerField(choices=STATUS,
                                    default=DRAFT,
                                    help_text="""Status""")

    author_view = models.ForeignKey("AuthorView",
                                     null=True)

    identifier = models.ForeignKey(Identifier)

    processing_id = models.CharField(max_length=128,blank=True)

    name = models.CharField(max_length=256)

    data = models.TextField(blank=True)

    user = models.ForeignKey(User,null=True)

    group = models.ForeignKey(Group)

    timestamp = models.DateTimeField()

    latest = models.BooleanField(default=False)

    @property
    def import_status(self):
        if self.processing_id:
            result = scheduled_import.AsyncResult(self.processing_id)
            if result:
                return result.status
            else:
                return 'n/a'

    @property
    def import_result(self):
        if self.processing_id:
            result = scheduled_import.AsyncResult(self.processing_id)
            if result.status == 'SUCCESS':
                try:
                    list_of_objects = result.get(timeout=1)
                    try:
                        top_level_obj_dict = list_of_objects[-1]
                        return top_level_obj_dict
                    except Exception:
                        return "Result of importer could not be interpreted."
                except Exception, e:
                    return "Import yielded exception %s" % e.message
            else:
                return None
        else:
            return None


    def __unicode__(self):
        return "%s (authored by user %s in group %s)" % (self.name,self.user, self.group)

    class Meta:
        unique_together = ("group",
                           "user",
                           "identifier",
                           "kind",
                           "timestamp")


    @staticmethod
    def object_copy(obj,**kwargs):
        """
        Copy a AuthoredData object with modifications as specified by key-value arguments
        in the kwargs (each key must correspond to one of the AuthoredDataObject model's
        attributes). The method makes sure that the 'latest' attribute is set correctly.

        """

        # We do not allow the user to specify the 'latest' attribute of the copied
        # object, since we take care of setting that correctly below.

        kwargs['latest'] = False

        # If no timestamp is provided in the kwargs, we default to now

        timestamp = kwargs.get('timestamp',timezone.now())

        # If no status is provided in the kwargs, the copied object will have the
        # same status as the existing object

        status = kwargs.get('status',obj.status)

        #
        # We retrieve the existing objects with same group and identifier
        #

        existing_objs = AuthoredData.objects.filter(group=obj.group,
                                                    identifier=obj.identifier)

        # We now find out how we have to set the  ``latest`` attribute




        # If the new object has status AUTOSAVE, latest is never touched.

        if status != AuthoredData.AUTOSAVE:

            younger_objs_count = existing_objs.exclude(status=AuthoredData.AUTOSAVE). \
                filter(timestamp__gt=timestamp).count()
            if not younger_objs_count:
                # The new object will be the most recent object, so we set the attribute
                # and remove a possible ``latest=True`` from all existing objects.
                kwargs['latest'] = True
                existing_objs.update(latest=False)
            else:
                kwargs['latest'] = False

        # We copy the object by setting the ``pk`` to None, changing what must be changed,
        # and saving the object.

        obj.pk = None
        for key in kwargs:
            setattr(obj,key,kwargs[key])
        obj.save()

        return obj


        authoring_data_obj.pk = None
        authoring_data_obj.latest = True
        authoring_data_obj.timestamp = timezone.now()
        authoring_data_obj.user = self.request.user
        authoring_data_obj.save()



    @staticmethod
    def object_create(kind=None,
                      status=None,
                      author_view='',
                      data=None,
                      user=None,
                      group=None,
                      identifier=None,
                      name=None,
                      timestamp=timezone.now(),
                      processing_id=''):

        if isinstance(identifier,basestring):
            identifier_obj, created = Identifier.objects.get_or_create(name=identifier)
        else:
            identifier_obj = identifier

        if isinstance(author_view,basestring):
            author_view_obj, created = AuthorView.objects.get_or_create(name=author_view)
        else:
            author_view_obj = author_view

        existing_objs = AuthoredData.objects.filter(group=group,
                                                    identifier=identifier_obj)

        latest=False

        if status != AuthoredData.AUTOSAVE:
            younger_objs_count = existing_objs.exclude(status=AuthoredData.AUTOSAVE).\
                                                       filter(timestamp__gt=timestamp).count()
            if not younger_objs_count:
                existing_objs.update(latest=False)
                latest= True

        return AuthoredData.objects.create(kind=kind,
                                           user=user,
                                           group=group,
                                           identifier=identifier_obj,
                                           status=status,
                                           author_view=author_view_obj,
                                           data=data,
                                           timestamp=timestamp,
                                           name=name,
                                           latest=latest,
                                           processing_id=processing_id)


    @staticmethod
    def object_update_OUTDATED(current_kind,
                      current_user,
                      current_group,
                      current_identifier,
                      current_timestamp,
                      **kwargs
                      ):


        if isinstance(current_identifier,basestring):
            current_identifier_obj, created = Identifier.objects.get_or_create(name=current_identifier)


        if 'identifier' in kwargs:
            identifier_value = kwargs['identifier']
            if isinstance(identifier_value,basestring):
                identifier_obj, created = Identifier.objects.get_or_create(name=identifier_value)
                kwargs['identifier'] = identifier_obj


        if 'author_view' in kwargs:
            author_view_value = kwargs['author_view']
            if isinstance(author_view_value,basestring):
                author_view_obj, created = AuthorView.objects.get_or_create(name=author_view_value)
                kwargs['author_view'] = author_view_obj



        objs = AuthoredData.objects.filter(kind=current_kind,
                                           user=current_user,
                                           group=current_group,
                                           identifier=current_identifier_obj)
        if current_timestamp == 'latest':
            objs = list(objs.order_by('-timestamp')[:1])
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


        return objs.update(**kwargs)

    @staticmethod
    def object_update_or_create_OUTDATED(current_kind,
                                current_user,
                                current_group,
                                current_identifier,
                                current_timestamp,
                                **kwargs):

        if current_timestamp == 'all':
            raise TypeError("This method cannot be called with timestamp = 'all'.")

        updated_objs = AuthoredData.object_update(current_kind,
                                                  current_user,
                                                  current_group,
                                                  current_identifier,
                                                  current_timestamp,
                                                  **kwargs)
        if updated_objs == 0:
            # no object was found, so we create one.

            if not 'identifier' in kwargs:
                kwargs['identifier'] = current_identifier
            if not 'kind' in kwargs:
                kwargs['kind'] = current_kind
            if not 'user' in kwargs:
                kwargs['user'] = current_user
            if not 'group' in kwargs:
                kwargs['group'] = current_group
            if not 'timestamp' in kwargs:
                if current_timestamp == 'latest':
                    kwargs['timestamp'] = timezone.now()
                else:
                    kwargs['timestamp'] = current_timestamp

            AuthoredData.object_create(**kwargs)


class InfoObject2AuthoredData(models.Model):
    iobject = models.OneToOneField(InfoObject,related_name = 'created_from_thru')
    authored_data = models.OneToOneField(AuthoredData)


