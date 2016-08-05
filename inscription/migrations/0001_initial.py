# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import inscription.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Eleve',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('indice', models.CharField(default=b'1', max_length=1)),
                ('nom', models.CharField(default=b'', max_length=100)),
                ('prenom', models.CharField(default=b'', max_length=100)),
                ('sexe', models.CharField(default=b'M', max_length=1)),
                ('date_naissance', models.DateField(null=True, blank=True)),
                ('email', models.EmailField(default=b'', max_length=254)),
                ('nom_etablissement', models.CharField(default=b'', max_length=50)),
                ('ville_etablissement', models.CharField(default=b'', max_length=20)),
                ('classe', models.CharField(default=b'', max_length=10)),
                ('adresse', models.TextField(default=b'')),
                ('code_postale', models.CharField(default=b'', max_length=5)),
                ('nom_responsable_legal', models.CharField(default=b'', max_length=20)),
                ('coordonnees_responsable_legal', models.TextField(default=b'')),
                ('inscription_complete', models.CharField(default=b'0', max_length=1, choices=[(b'1', b'Oui'), (b'0', b'Non')])),
                ('autorisations_completees', models.CharField(default=b'0', max_length=1, choices=[(b'1', b'Oui'), (b'0', b'Non')])),
                ('paiement_valide', models.CharField(default=b'0', max_length=1, choices=[(b'1', b'Oui'), (b'0', b'Non')])),
                ('paiement_description', models.TextField(default=b'')),
                ('fiche_sanitaire', models.FileField(default=b'blank.pdf', upload_to=inscription.models.renommage_fiche_sanitaire1)),
                ('autorisation_parentale', models.FileField(default=b'blank.pdf', upload_to=inscription.models.renommage_autorisation_parentale1)),
                ('autorisation_photo', models.FileField(default=b'blank.pdf', upload_to=inscription.models.renommage_autorisation_photo1)),
                ('fiche_sanitaire_version2', models.FileField(default=b'blank.pdf', upload_to=inscription.models.renommage_fiche_sanitaire2)),
                ('autorisation_parentale_version2', models.FileField(default=b'blank.pdf', upload_to=inscription.models.renommage_autorisation_parentale2)),
                ('autorisation_photo_version2', models.FileField(default=b'blank.pdf', upload_to=inscription.models.renommage_autorisation_photo2)),
            ],
        ),
        migrations.CreateModel(
            name='Encadrant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('indice', models.CharField(default=b'1', max_length=1)),
                ('nom', models.CharField(default=b'', max_length=20)),
                ('prenom', models.CharField(default=b'', max_length=20)),
                ('sexe', models.CharField(default=b'M', max_length=1)),
                ('email', models.EmailField(default=b'', max_length=254)),
                ('profession', models.TextField(default=b'')),
                ('presence', models.CharField(default=b'1', max_length=3, choices=[(b'1', b'Oui'), (b'0', b'Non')])),
                ('inscription_complete', models.CharField(default=b'0', max_length=1, choices=[(b'1', b'Oui'), (b'0', b'Non')])),
            ],
        ),
        migrations.CreateModel(
            name='Equipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom_equipe', models.CharField(max_length=200)),
                ('trigramme', models.CharField(default=b'TES', max_length=3)),
                ('nombre_encadrants', models.CharField(default=b'2', max_length=1)),
                ('nombre_eleves', models.CharField(default=b'6', max_length=1)),
                ('inscription_ouverte', models.CharField(default=b'1', max_length=1)),
                ('inscription_complete', models.CharField(default=b'0', max_length=1)),
                ('inscription_validee', models.CharField(default=b'0', max_length=1, choices=[(b'0', b'En attente'), (b'1', b'Valider la s\xc3\xa9lection'), (b'2', b'Annuler la s\xc3\xa9lection')])),
                ('connexion', models.CharField(default=b'1', max_length=1)),
                ('code_donnee', models.CharField(default=b'0', max_length=18)),
                ('autorisations_completees', models.CharField(default=b'0', max_length=1)),
            ],
            options={
                'permissions': (('inscrit', 'Equipe inscrite'),),
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=100, null=True, blank=True)),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('action', models.TextField(default=b'', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organisateur',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('connexion', models.CharField(default=b'1', max_length=b'1')),
                ('numero_fixe', models.CharField(default=b'', max_length=b'10', blank=True)),
                ('numero_portable', models.CharField(default=b'', max_length=b'10', blank=True)),
                ('description', models.TextField(default=b'', blank=True)),
                ('code_donnee', models.CharField(default=b'0', max_length=18)),
                ('mdp_time', models.DateField(null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('admin', "Etre l'admin"), ('organisateur', 'Etre un organisateur'), ('paiement', 'Valider paiement')),
            },
        ),
        migrations.CreateModel(
            name='Probleme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.CharField(max_length=1)),
                ('version', models.CharField(max_length=1)),
                ('fichier', models.FileField(default=b'blank.pdf', upload_to=inscription.models.renommage_probleme)),
                ('equipe', models.ForeignKey(to='inscription.Equipe')),
            ],
        ),
        migrations.CreateModel(
            name='Tournoi',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lieu', models.CharField(max_length=20)),
                ('dates', models.DateField(null=True, blank=True)),
                ('dates_fin', models.DateField(null=True, blank=True)),
                ('description', models.TextField(default=b'')),
                ('nombre_problemes', models.CharField(default=b'1', max_length=2)),
                ('date_limite', models.DateField(null=True, blank=True)),
                ('date_limite_def', models.DateField(null=True, blank=True)),
                ('nombre_equipes_validees_max', models.CharField(default=b'10', max_length=2)),
                ('organisateurs', models.TextField(default=b'')),
            ],
        ),
        migrations.AddField(
            model_name='equipe',
            name='tournoi',
            field=models.ForeignKey(to='inscription.Tournoi'),
        ),
        migrations.AddField(
            model_name='equipe',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='encadrant',
            name='equipe',
            field=models.ForeignKey(to='inscription.Equipe'),
        ),
        migrations.AddField(
            model_name='eleve',
            name='equipe',
            field=models.ForeignKey(to='inscription.Equipe'),
        ),
    ]
