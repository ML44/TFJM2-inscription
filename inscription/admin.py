#-*- coding: utf-8 -*-

from django.contrib import admin

from inscription.models import *


from import_export import resources
from import_export.admin import ImportExportModelAdmin

from import_export import fields

from import_export.widgets import ForeignKeyWidget



admin.site.register(Organisateur)


class EquipeResource(resources.ModelResource):
	tournoi = fields.Field(column_name='Tournoi',attribute='tournoi',widget=ForeignKeyWidget(Tournoi,'lieu'))
	user = fields.Field(column_name='Username',attribute='user',widget=ForeignKeyWidget(User,'username'))
	class Meta:
		model = Equipe
		fields = ('nom_equipe','trigramme','tournoi','nombre_encadrants','nombre_eleves',)

class EleveResource(resources.ModelResource):
	equipe = fields.Field(column_name='Equipe',attribute='equipe',widget=ForeignKeyWidget(Equipe,'nom_equipe'))
	class Meta:
		model = Eleve
        fields = ('nom','prenom','sexe','email','date_naissance','nom_etablissement','ville_etablissement','classe','adresse',
         'code_postale', 'nom_responsable_legal', 'coordonnees_responsable_legal','inscription_complete','autorisations_completees',
         'paiement_valide','paiement_description')

class Encadrant1Resource(resources.ModelResource):
	equipe = fields.Field(column_name='Equipe',attribute='equipe',widget=ForeignKeyWidget(Equipe,'nom_equipe'))
	class Meta:
		model = Eleve
		fields = ('nom','prenom','sexe','email','date_naissance','nom_etablissement','ville_etablissement','classe','adresse',
         'code_postale', 'nom_responsable_legal', 'coordonnees_responsable_legal','inscription_complete','autorisations_completees',)

class EncadrantResource(resources.ModelResource):
	equipe = fields.Field(column_name='Equipe',attribute='equipe',widget=ForeignKeyWidget(Equipe,'nom_equipe'))
	class Meta:
		model = Encadrant
		fields = ('nom','prenom','sexe','email','profession','presence','inscription_complete')

class LogResource(resources.ModelResource):

    class Meta:
        model = Log