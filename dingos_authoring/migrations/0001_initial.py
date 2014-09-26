# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('dingos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthoredData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kind', models.SmallIntegerField(default=0, help_text=b'Type of data', choices=[(0, b'JSON (Dingos Authoring)'), (1, b'XML')])),
                ('status', models.SmallIntegerField(default=0, help_text=b'Status', choices=[(0, b'Draft'), (1, b'Imported'), (2, b'Update (not yet imported)'), (3, b'Autosave')])),
                ('processing_id', models.CharField(max_length=128, blank=True)),
                ('name', models.CharField(max_length=256)),
                ('data', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField()),
                ('latest', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuthorView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'View Identifier', unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupNamespaceMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allowed_namespaces', models.ManyToManyField(help_text=b'List of identifier namespaces in which objects may be authored or imported by users of group.', related_name=b'authoring_allowed_for', to='dingos.IdentifierNameSpace', blank=True)),
                ('default_namespace', models.ForeignKey(related_name=b'authoring_default_for', to='dingos.IdentifierNameSpace', help_text=b'Identifier namespace to be used when authoring new STIX/Cybox document.')),
                ('group', models.OneToOneField(to='auth.Group', help_text=b'Group for which this mapping defines default namespace and allowed namespaces.')),
            ],
            options={
                'verbose_name': 'Group-2-Identifier-Namespace Mapping',
                'verbose_name_plural': 'Group-2-Identifier-Namespace Mappings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Identifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Name/Identifier', unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserAuthoringInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('default_authoring_namespace_info', models.ForeignKey(to='dingos_authoring.GroupNamespaceMap')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='authoreddata',
            name='author_view',
            field=models.ForeignKey(to='dingos_authoring.AuthorView', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authoreddata',
            name='group',
            field=models.ForeignKey(to='auth.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authoreddata',
            name='identifier',
            field=models.ForeignKey(to='dingos_authoring.Identifier'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authoreddata',
            name='top_level_iobject',
            field=models.ForeignKey(related_name=b'top_level_of', to='dingos.InfoObject', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authoreddata',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authoreddata',
            name='yielded',
            field=models.OneToOneField(related_name=b'yielded_by', null=True, to='dingos_authoring.AuthoredData'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authoreddata',
            name='yielded_iobjects',
            field=models.ManyToManyField(related_name=b'yielded_by', to='dingos.InfoObject'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='authoreddata',
            unique_together=set([('group', 'user', 'identifier', 'kind', 'timestamp')]),
        ),
    ]
