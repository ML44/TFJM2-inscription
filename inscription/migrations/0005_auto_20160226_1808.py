# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import inscription.models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0004_auto_20160226_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eleve',
            name='email',
            field=models.EmailField(default=b'', max_length=254),
        ),
        migrations.AlterField(
            model_name='eleve',
            name='fiche_sanitaire_version2',
            field=models.FileField(default=b'blank.pdf', max_length=301, upload_to=inscription.models.renommage_fiche_sanitaire2),
        ),
        migrations.AlterField(
            model_name='encadrant',
            name='email',
            field=models.EmailField(default=b'', max_length=254),
        ),
    ]
