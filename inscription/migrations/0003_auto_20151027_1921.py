# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0002_auto_20150922_2056'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipe',
            name='date_validation',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='equipe',
            name='trigramme',
            field=models.CharField(default=b'T', max_length=3),
        ),
    ]
