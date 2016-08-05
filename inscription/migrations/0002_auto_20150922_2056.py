# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='probleme',
            name='numero',
            field=models.CharField(max_length=2),
        ),
        migrations.AlterField(
            model_name='probleme',
            name='version',
            field=models.CharField(max_length=2),
        ),
    ]
