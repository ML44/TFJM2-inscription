#-*- coding: utf-8 -*-

from django import forms
from inscription.models import *
from django.utils.translation import ugettext_lazy as _

import os

import floppyforms as forms


class DatePicker(forms.DateInput):

    class Media:
        js = (
            'js/jquery.min.js',
            'js/jquery-ui.min.js',
        )
        css = {
            'all': (
                'css/jquery-ui.css',
            )
        }

class connexion_form(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

class mdp_form(forms.Form):
	username = forms.CharField(label = "Nom d'utilisateur", required = True)
	email = forms.EmailField(label = "Votre e-mail", required = True)

class nouveau_mdp_form(forms.Form):
	password = forms.CharField(label="Nouveau mot de passe", widget=forms.PasswordInput)
	password_conf = forms.CharField(label="Confirmez le nouveau mot de passe", widget=forms.PasswordInput)

class ajouter_tournoi_form(forms.ModelForm):
    class Meta:
		model = Tournoi
		fields = ('lieu', 'dates', 'dates_fin', 'description', 'nombre_problemes', 'date_limite', 'date_limite_def','nombre_equipes_validees_max','organisateurs')

		labels = {
			'lieu': _("Lieu du tournoi"),
			'dates': _(u"Date de début du tournoi"),
			'dates_fin': _("Date de fin du tournoi"),
			'description': _(u"Description"),
			'nombre_problemes': _("Nombres de problemes"),
			'date_limite': _(u"Date limite d'inscription à ce tournoi"),
			'date_limite_def': _(u"Date limite pour les problèmes et autorisations"),
			'nombre_equipes_validees_max': _(u"Nombre maximum d'équipes inscrites au tournoi"),
			'organisateurs': _(u"Organisateurs"),
		}

		widgets = {
		        'dates': forms.DateInput(),
                'dates_fin': forms.DateInput(),
		        'date_limite_def': forms.DateInput(),
		        'date_limite': forms.DateInput(),
	    	}


class modifier_tournoi_form(forms.ModelForm):
	class Meta:
		model = Tournoi
		fields = ('dates', 'dates_fin', 'description', 'date_limite', 'date_limite_def','nombre_equipes_validees_max','organisateurs')

		labels = {
			'dates': _(u"Date de début du tournoi"),
			'dates_fin': _("Date de fin du tournoi"),
			'description': _(u"Description"),
			'date_limite': _(u"Date limite d'inscription à ce tournoi"),
			'date_limite_def': _(u"Date limite pour les problèmes et autorisations"),
			'nombre_equipes_validees_max': _(u"Nombre maximum d'équipes inscrites au tournoi"),
			'organisateurs': _(u"Organisateurs"),
		}

		widgets = {
		        'dates': forms.DateInput(),
		        'dates_fin': forms.DateInput(),
		        'date_limite_def': forms.DateInput(),
		        'date_limite': forms.DateInput(),
	    	}



class Inscription_Eleve(forms.ModelForm):
	class Meta:
			model = Eleve
			fields = ('nom','prenom','sexe', 'date_naissance', 'email','nom_etablissement','ville_etablissement',
				'classe','adresse','code_postale','nom_responsable_legal','coordonnees_responsable_legal')
			labels = {
				'nom': _("Nom"),
				'prenom': _(u"Prénom"),
				'date_naissance': _("Date de naissance"),
				'sexe': _("Sexe"),
				'email': _("Adresse mail"),
				'nom_responsable_legal': _(u"Nom du responsable légal"),
				'code_postale': _("Code postal"),
				'adresse': _("Adresse postale"),
				'ville_etablissement': _(u"Ville de l'établissement scolaire fréquenté"),
				'nom_etablissement': _(u"Nom de l'établissement scolaire fréquenté"),
				'classe': _("Classe"),
				'coordonnees_responsable_legal': _(u"Coordonnées du responsable légal"),

			}

			widgets = {
		        'sexe':  forms.Select( choices = ( ('M','M') , ('F','F') ) ),
		        'classe': forms.Select( choices = ( ("2nde","2nde") , ("1ere S","1ere S") , ("Tle S","Tle S") ) ),
		        'date_naissance': forms.DateInput(),
	    	}

			help_texts = {
		    	'coordonnees_responsable_legal': _(u"Si autres que précédentes - Précisez une adresse et un numéro de téléphone -"),
    		}

class Inscription_Encadrant(forms.ModelForm):
	class Meta:
			model = Encadrant
			fields = ('nom','prenom','sexe','email','profession','presence')
			labels = {
				'nom': _("Nom"),
				'prenom': _(u"Prénom"),
				'sexe': _("Sexe"),
				'email': _("Adresse mail"),
				'profession': _(u"Profession / Lien avec l'équipe"),
				'presence': _(u"L'encadrant pourra être présent pendant le tournoi régional"),
			}

			widgets = {
	        'sexe':  forms.Select( choices = ( ('M','M') , ('F','F') ) ),
	        'presence': forms.Select( choices = ( (1,'Oui') , (0,'Non') ) ),
	    	}

class Equipe_Form(forms.ModelForm):
	class Meta:
			model = Equipe
			fields = ('nombre_eleves', 'nombre_encadrants', 'tournoi')
			labels = {
				'nombre_encadrants': _("Nombre d'encadrants"),
				'nombre_eleves': _(u"Nombre d'élèves"),
				'tournoi': _("Tournoi"),
			}

			widgets = {
	        'nombre_eleves': forms.Select(choices = ( ('4','4') , ('5','5') , ('6','6') ) ),
	    	}


class ajouter_organisateur_form(forms.Form):
	username = forms.CharField(label="Pseudo")
	nom = forms.CharField(label="Nom", max_length = 30)
	prenom = forms.CharField(label="Prénom",max_length = 30)
	email = forms.EmailField(label="Email")

class changer_mdp_organisateur_form(forms.Form):
	password = forms.CharField(label = "Mot de Passe", widget=forms.PasswordInput)
	password_conf = forms.CharField(label = "Confirmez votre mot de passe", widget=forms.PasswordInput)


class changer_mdp_admin_form(forms.Form):
	password = forms.CharField(label = "Mot de Passe", widget=forms.PasswordInput)
	password_conf = forms.CharField(label = "Confirmez votre mot de passe", widget=forms.PasswordInput)



class profil_organisateur_form(forms.ModelForm):
	email = forms.EmailField(label="Email (si changement)", required=False)
	class Meta:
		model = Organisateur
		fields = ('numero_portable','numero_fixe','description')
		labels = {
			'numero_portable': _(u"Numéro de portable"),
			'numero_fixe': _(u"Numéro fixe"),
			'description': _("Description (Profession, occupation, etc.)"),
		}


class Inscription_Equipe_def(forms.Form):
	username = forms.CharField(label="Nom de l'équipe", max_length=30)
	email = forms.EmailField(label="Email", required = True)

class Inscription_Equipe(forms.ModelForm):
	class Meta:
		model = Equipe
		fields = ('tournoi',)
		labels = {
			'tournoi': _("Choissisez un tournoi"),
		}

class mdp_connexion_form(forms.Form):
	password = forms.CharField(label = "Veuillez entrer un mot de passe", widget=forms.PasswordInput)
	password_conf = forms.CharField(label = "Confirmez votre mot de passe", widget=forms.PasswordInput)

class validation_equipe_form(forms.ModelForm):
	class Meta:
		model = Equipe
		fields = ('trigramme','inscription_validee',)
		labels = {
			'trigramme': _("Veuillez attribuer un trigramme à cette équipe (autre que ZZZ)"),
			'inscription_validee': _("Sélection de l'équipe"),
		}


class supprimer1_equipe_form(forms.Form):
	vide = forms.CharField(max_length=1)


class supprimer1_organisateur_form(forms.Form):
	vide = forms.CharField(max_length=1)

class modifier_permission_form(forms.Form):
	permission = forms.CharField(label="", max_length=10, widget = forms.Select(choices = ( ('1','Lecture') , ('2','Ecriture'), ('3','Rien') ) ) )
	permission_paiement = forms.CharField(label=" Paiement:", max_length=10, widget = forms.Select(choices = ( ('1','Oui') , ('2','Non') ) ) )


class MonCompte(forms.Form):
	new_email = forms.EmailField(label="Nouvel e-mail", required=False)
	old_pwd = forms.CharField(label="Veuillez saisir votre mot de passe", widget=forms.PasswordInput,required=False)

class MonCompteB(forms.Form):
	nombre_encadrants = forms.CharField(required=False, max_length=1, label = "Nombre d'encadrants", widget = forms.Select(choices = ( ('1','1') , ('2','2') ) ))
	nombre_eleves = forms.CharField(required=False, max_length=1, label = "Nombre d'élèves", widget = forms.Select(choices = ( ('4','4') , ('5','5') , ('6','6') )))


class MonCompteC(forms.Form):
	old_pwd = forms.CharField(label="Ancien mot de passe", widget=forms.PasswordInput, required=False)
	new_pwd = forms.CharField(label="Nouveau mot de passe", widget=forms.PasswordInput, required=False)
	new_pwd_cf = forms.CharField(label="Réécrire le nouveau mot de passe", widget=forms.PasswordInput, required=False)



class changer_mdp_orga_form(forms.Form):
	old_pwd = forms.CharField(label="Ancien mot de passe", widget=forms.PasswordInput, required=False)
	new_pwd = forms.CharField(label="Nouveau mot de passe", widget=forms.PasswordInput, required=False)
	new_pwd_cf = forms.CharField(label="Réécrire le nouveau mot de passe", widget=forms.PasswordInput, required=False)

class Vide(forms.Form):
	vide = forms.CharField(max_length=1)


class profil_paiement_form(forms.ModelForm):
	class Meta:
		model = Eleve
		fields = ('paiement_valide','paiement_description',)
		labels = {
			'paiement_valide': _("L'élève a-t-il payé?"),
			'paiement_description': _("Mode de paiement:"),
		}


from django.template.defaultfilters import filesizeformat

class ExtFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.max_upload_size = kwargs.pop('max_upload_size', None)
        self.ext_whitelist = [i.lower() for i in ext_whitelist]

        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
	    data = super(ExtFileField, self).clean(*args, **kwargs)
	    if data:
	        filename = data.name
	        ext = os.path.splitext(filename)[1]
	        ext = ext.lower()
	        if ext not in self.ext_whitelist:
	            raise forms.ValidationError("Types de fichier acceptés: " + ', '.join(self.ext_whitelist))
	    	if data.size > self.max_upload_size:
	    	    raise forms.ValidationError("Le fichier est de taille trop grande.")

	    return data

#-------------------------------------------------------------------------

if __name__ == "__main__":
    import doctest, datetime
    doctest.testmod()





class AutorisationsForm(forms.Form):
	fiche_sanitaire = ExtFileField(ext_whitelist=(".pdf",), label = "Fiche Sanitaire de Liaison", max_upload_size=8388608, required = False)
	autorisation_parentale = ExtFileField(ext_whitelist=(".pdf",), label = "Autorisation parentale pour les mineurs", max_upload_size=8388608, required = False)
	autorisation_photo = ExtFileField(ext_whitelist=(".pdf",), label = "Autorisation de reproduction et de représentation de prises de vue", max_upload_size=8388608, required = False)
	majeur = forms.BooleanField(label="Cet élève aura plus de 18 ans lors du tournoi:", required=False)

class Probleme_Form(forms.Form):
	probleme = ExtFileField(ext_whitelist=(".pdf",), label = "", max_upload_size=5242880, required = False)


