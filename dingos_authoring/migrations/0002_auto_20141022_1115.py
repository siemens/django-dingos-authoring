# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dingos_authoring', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='authoreddata',
            name='storage_location',
            field=models.SmallIntegerField(default=0, help_text=b'Where the data is stored', choices=[(0, b'Database'), (1, b'Filesystem')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='authoreddata',
            name='group',
            field=models.ForeignKey(to='auth.Group', null=True),
        ),
    ]
