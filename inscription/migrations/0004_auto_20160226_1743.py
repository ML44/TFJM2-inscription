# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import inscription.models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0003_auto_20151027_1921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eleve',
            name='autorisation_parentale',
            field=models.FileField(default=b'blank.pdf', max_length=300, upload_to=inscription.models.renommage_autorisation_parentale1),
        ),
        migrations.AlterField(
            model_name='eleve',
            name='autorisation_parentale_version2',
            field=models.FileField(default=b'blank.pdf', max_length=300, upload_to=inscription.models.renommage_autorisation_parentale2),
        ),
        migrations.AlterField(
            model_name='eleve',
            name='autorisation_photo',
            field=models.FileField(default=b'blank.pdf', max_length=300, upload_to=inscription.models.renommage_autorisation_photo1),
        ),
        migrations.AlterField(
            model_name='eleve',
            name='autorisation_photo_version2',
            field=models.FileField(default=b'blank.pdf', max_length=300, upload_to=inscription.models.renommage_autorisation_photo2),
        ),
        migrations.AlterField(
            model_name='eleve',
            name='email',
            field=models.EmailField(default=b'', max_length=75),
        ),
        migrations.AlterField(
            model_name='eleve',
            name='fiche_sanitaire',
            field=models.FileField(default=b'blank.pdf', max_length=300, upload_to=inscription.models.renommage_fiche_sanitaire1),
        ),
        migrations.AlterField(
            model_name='eleve',
            name='fiche_sanitaire_version2',
            field=models.FileField(default=b'blank.pdf', max_length=300, upload_to=inscription.models.renommage_fiche_sanitaire2),
        ),
        migrations.AlterField(
            model_name='encadrant',
            name='email',
            field=models.EmailField(default=b'', max_length=75),
        ),
        migrations.AlterField(
            model_name='probleme',
            name='fichier',
            field=models.FileField(default=b'blank.pdf', max_length=300, upload_to=inscription.models.renommage_probleme),
        ),
    ]
