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


from django.contrib import admin

from models import AuthoredData, GroupNamespaceMap, AuthorView



#
# Inline Interfaces
# -----------------
#
# Django offers the possibility to enrich an admin
# interfaces with admin areas for related objects
# that are 'inlined' into the main interface.
# To achieve this, Inline-classes have to
# be defined.
#
# We use the following naming convention:
#
# XXXXXXX[_zzzzzz_][_]YYYYYYYInline
#
# means that object XXXXXX contains an inline for object YYYYYYYY.
# 'zzzzzz' may be used if the same YYYYYY object is inlined in several
# ways according to multiple relations between XXXXXX and YYYYYY -- see
# examples below).  Underbars may be used to separate names where
# camel-casing gets to confusing.
#
# In inline interface, use the properties 'verbose_name' and 'verbose_name_plural'
# to provide information about the way in which inlines are related to the
# main object.
#
#



#
# Admin Interfaces
# ----------------
#
# Below we specify admin interfaces in which
# we tweak the behavior of the standard admin
# interface:
#
# - list_display: which fields to display in the list of objects
# - list_filter: which fields can be used for filtering the list of objects
# - inlines: which admin interfaces should be inlined?
#
# We also hook into the save-on-change/create mechanism
# to do additional changes where necessary.
#
#


#
# Registration
# ------------
#
# Below, we register admin interfaces.
#



admin.site.register(AuthoredData)
admin.site.register(AuthorView)
admin.site.register(GroupNamespaceMap)


