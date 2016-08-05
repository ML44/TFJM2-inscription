#-*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from randomfilestorage.storage import RandomFileSystemStorage

#from phonenumber_field.modelfields import PhoneNumberField

from random import *
import os

def renommage_probleme(instance, nom):
	alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	url = ''.join(choice(alphabet) for i in range(20))
	nom_fichier = os.path.splitext(nom)[0]
	url_vrai = instance.equipe.nom_equipe + "/" + "problemes" + "/" + instance.numero + "/" + instance.version + "/" + url
	return url_vrai+"/{}".format(nom_fichier)

def renommage_fiche_sanitaire1(instance, nom):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    url = ''.join(choice(alphabet) for i in range(20))
    nom_fichier = os.path.splitext(nom)[0]
    url_vrai = instance.equipe.nom_equipe + "/" + "fiche_sanitaire"+ "/" + instance.indice + "/" + "1" + "/" + url
    return url_vrai+"/{}".format(nom_fichier)

def renommage_autorisation_parentale1(instance, nom):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    url = ''.join(choice(alphabet) for i in range(20))
    nom_fichier = os.path.splitext(nom)[0]
    url_vrai = instance.equipe.nom_equipe + "/" + "autorisation_parentale"+ "/" + instance.indice + "/" + "1" + "/" + url
    return url_vrai+"/{}".format(nom_fichier)

def renommage_autorisation_photo1(instance, nom):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    url = ''.join(choice(alphabet) for i in range(20))
    nom_fichier = os.path.splitext(nom)[0]
    url_vrai = instance.equipe.nom_equipe + "/" + "autorisation_photo"+ "/" + instance.indice + "/" + "1" + "/" + url
    return url_vrai+"/{}".format(nom_fichier)

def renommage_fiche_sanitaire2(instance, nom):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    url = ''.join(choice(alphabet) for i in range(20))
    nom_fichier = os.path.splitext(nom)[0]
    url_vrai = instance.equipe.nom_equipe + "/" + "fiche_sanitaire"+ "/" + instance.indice + "/" + "2" + "/" + url
    return url_vrai+"/{}".format(nom_fichier)

def renommage_autorisation_parentale2(instance, nom):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    url = ''.join(choice(alphabet) for i in range(20))
    nom_fichier = os.path.splitext(nom)[0]
    url_vrai = instance.equipe.nom_equipe + "/" + "autorisation_parentale"+ "/" + instance.indice + "/" + "2" + "/" + url
    return url_vrai+"/{}".format(nom_fichier)

def renommage_autorisation_photo2(instance, nom):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    url = ''.join(choice(alphabet) for i in range(20))
    nom_fichier = os.path.splitext(nom)[0]
    url_vrai = instance.equipe.nom_equipe + "/" + "autorisation_photo"+ "/" + instance.indice + "/" + "2" + "/" + url
    return url_vrai+"/{}".format(nom_fichier)

class Equipe(models.Model):
	user = models.OneToOneField(User)
	tournoi = models.ForeignKey('Tournoi')

	nom_equipe = models.CharField(max_length=200)
	trigramme = models.CharField(max_length=3, default="T")
	nombre_encadrants = models.CharField(max_length=1, default = '2')
	nombre_eleves = models.CharField(max_length = 1, default = '6')

	inscription_ouverte = models.CharField(max_length = 1, default = '1')
	inscription_complete = models.CharField(max_length = 1, default = '0')

	ATTENTE = '0'
	VALIDER_SELECTION = '1'
	ANNULER_SELECTION = '2'

	VALIDATION_CHOICES = (
		(ATTENTE, 'En attente'),
		(VALIDER_SELECTION, 'Valider la sélection'),
		(ANNULER_SELECTION, 'Annuler la sélection'),
	)

	inscription_validee = models.CharField(max_length = 1, choices = VALIDATION_CHOICES, default = ATTENTE)

	connexion = models.CharField(max_length = 1, default = '1')
	code_donnee = models.CharField(max_length = 18, default = '0')

	autorisations_completees = models.CharField(max_length = 1, default = '0')

	date_validation = models.DateField(null = True, blank = True)

	def __str__(self):
		return self.nom_equipe

	class Meta:
		permissions = (
			("inscrit", "Equipe inscrite"),
		)

class Probleme(models.Model):
	numero = models.CharField(max_length = 2)
	equipe = models.ForeignKey('Equipe')
	version = models.CharField(max_length = 2)
	fichier = models.FileField(upload_to=renommage_probleme,default = 'blank.pdf',max_length = 300,)

	def __str__(self):
		return self.numero

class Encadrant(models.Model):
	equipe = models.ForeignKey('Equipe')
	indice = models.CharField(max_length = 1, default = '1')

	OUI = '1'
	NON = '0'

	VALIDATION_CHOICES = (
		(OUI, 'Oui'),
		(NON, 'Non'),

	)

	nom = models.CharField(max_length = 20, default = '', )
	prenom = models.CharField(max_length = 20, default = '', )
	sexe = models.CharField(max_length = 1, default = 'M', )
	email = models.EmailField(default = '', )
	profession = models.TextField(default = '', )
	presence = models.CharField(max_length = 3,choices = VALIDATION_CHOICES, default = OUI)

	inscription_complete = models.CharField(max_length = 1,choices = VALIDATION_CHOICES, default = NON)


	def __str__(self):
		return self.nom

class Eleve(models.Model):
	equipe = models.ForeignKey('Equipe')
	indice = models.CharField(max_length = 1, default = '1')

	nom = models.CharField(max_length=100, default = '')
	prenom = models.CharField(max_length=100, default = '')
	sexe = models.CharField(max_length = 1, default = 'M')
	date_naissance = models.DateField(blank=True, null = True)
	email = models.EmailField(default = '', )
	nom_etablissement = models.CharField(max_length = 50,default = '')
	ville_etablissement = models.CharField(max_length = 20, default = '')
	classe = models.CharField(max_length = 10, default = '')
	adresse = models.TextField(default = '')
	code_postale = models.CharField(max_length = 5, default = '')
	nom_responsable_legal = models.CharField(max_length = 20, default = '')
	coordonnees_responsable_legal = models.TextField(default = '')

	OUI = '1'
	NON = '0'

	VALIDATION_CHOICES = (
		(OUI, 'Oui'),
		(NON, 'Non'),

	)

	inscription_complete = models.CharField(max_length = 1, choices = VALIDATION_CHOICES, default = NON)

	autorisations_completees = models.CharField(max_length = 1, choices = VALIDATION_CHOICES, default = NON)

	paiement_valide = models.CharField(max_length = 1, choices = VALIDATION_CHOICES, default = NON)

	paiement_description = models.TextField(default = '')

	fiche_sanitaire = models.FileField(
        upload_to=renommage_fiche_sanitaire1, default = 'blank.pdf', max_length = 300,
    )
	autorisation_parentale = models.FileField(
        upload_to=renommage_autorisation_parentale1, default = 'blank.pdf', max_length = 300,
    )
	autorisation_photo = models.FileField(
        upload_to=renommage_autorisation_photo1, default = 'blank.pdf', max_length = 300,
    )

	fiche_sanitaire_version2 = models.FileField(
		upload_to=renommage_fiche_sanitaire2, default = 'blank.pdf', max_length = 301,
		)
	autorisation_parentale_version2 = models.FileField(
		upload_to=renommage_autorisation_parentale2, default = 'blank.pdf', max_length = 300,
		)
	autorisation_photo_version2 = models.FileField(
		upload_to=renommage_autorisation_photo2, default = 'blank.pdf', max_length = 300,
		)

	def __str__(self):
		return self.nom

class Tournoi(models.Model):
	lieu = models.CharField(max_length = 20)
	dates = models.DateField(blank = True, null = True)
	dates_fin = models.DateField(blank = True, null = True)
	description = models.TextField(default = '')

	nombre_problemes = models.CharField(max_length = 2, default = '1')

	date_limite = models.DateField(null = True, blank = True)
	date_limite_def = models.DateField(null = True, blank = True)

	nombre_equipes_validees_max = models.CharField(max_length = 2, default = '10')
	organisateurs = models.TextField(default = '')

	def __str__(self):
		return self.lieu

class Organisateur(models.Model):
	user = models.OneToOneField(User)
	connexion = models.CharField(default = '1', max_length = '1')

	numero_fixe = models.CharField(max_length = '10', default = '', blank = True)
	numero_portable = models.CharField(max_length = '10', default = '', blank = True)
	description = models.TextField(default = '', blank = True)

	code_donnee = models.CharField(max_length = 18, default = '0')

	mdp_time = models.DateField(null = True)

	def __str__(self):
		return self.user.last_name

	class Meta:
		permissions = (
			("admin","Etre l'admin"),
			("organisateur","Etre un organisateur"),
			("paiement", "Valider paiement"),
		)


class Log(models.Model):
	user = models.CharField(max_length = 100, null = True, blank = True)
	timestamp = models.DateTimeField(null = True, blank = True)
	action = models.TextField(default = '', blank = True)

	def __str__(self):
		return self.user.last_name