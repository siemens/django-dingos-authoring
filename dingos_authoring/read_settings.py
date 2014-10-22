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

from django.conf import settings
from django.core.files.storage import FileSystemStorage

import dingos_authoring

if settings.configured and 'DINGOS_AUTHORING' in dir(settings):
    dingos_authoring.DINGOS_AUTHORING_IMPORTER_REGISTRY = settings.DINGOS_AUTHORING.get('IMPORTER_REGISTRY', dingos_authoring.DINGOS_AUTHORING_IMPORTER_REGISTRY)

if settings.configured and 'DINGOS_AUTHORING' in dir(settings):
    dingos_authoring.DINGOS_AUTHORING_CELERY_BUG_WORKAROUND = settings.DINGOS_AUTHORING.get('CELERY_BUG_WORKAROUND', dingos_authoring.DINGOS_AUTHORING_CELERY_BUG_WORKAROUND)


if settings.configured and 'DINGOS_AUTHORING' in dir(settings):

    if not "DATA_FILESYSTEM_ROOT" in settings.DINGOS_AUTHORING:
        raise NotImplementedError("Please configure a DATA_FILESYSTEM_ROOT  directory in the DINGOS_AUTHORING settings (look "
                                  "at how the MEDIA directory is defined and define an appropriate directory "
                                  "for storing authored data (usually imported XMLs) on the filesystem. "
                                  "Example setting : root('authoring','imports')")

else:
    dingos_authoring.DINGOS_AUTHORING_DATA_FILESYSTEM_ROOT = settings.DINGOS_AUTHORING['DATA_FILESYSTEM_ROOT']

    dingos_authoring.DINGOS_AUTHORING_DATA_STORAGE = FileSystemStorage(location=dingos_authoring.DINGOS_AUTHORING_DATA_FILESYSTEM_ROOT)
    # We do not want the blobs to be directly available via URL.
    # Reading the code it seems that setting 'base_url=None' in
    # the __init__ arguments does not help, because __init__
    # then choses the media URL as default url. So we have
    # to set it explicitly after __init__ is done.
    dingos_authoring.DINGOS_AUTHORING_DATA_STORAGE.base_url=None