#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include


urlpatterns = patterns('inscription.views',
	url(r'^home$', 'home'),
    url(r'^tournois$', 'liste_des_tournois'),
    url(r'^tournois/(?P<lieu>.*)$','tournoi'),
    url(r'^tournois-connecte/(?P<lieu>.*)$','tournoi_connecte'),
    url(r'^connexion$', 'connexion'),
    url(r'^motdepasseoublie$', 'mdp_oublie'),
    url(r'^mdp/(?P<code_donnee>.*)/(?P<username>.*)$', 'mdp'),
    url(r'^deconnexion$', 'deconnexion'),

    url(r'^ajouter_tournoi$', 'ajouter_tournoi'),
    url(r'^organisateurs$', 'liste_organisateur'),
    url(r'^lire_profile_organisateur/(?P<organisateur_last_name>.*)/(?P<organisateur_first_name>.*)$', 'lire_profile_organisateur'),
    url(r'^ajouter_organisateur$', 'ajouter_organisateur'),


    url(r'^supprimer_organisateur/(?P<nom>.*)/(?P<prenom>.*)$', 'supprimer_organisateur'),
    url(r'^supprimer_organisateur_vrai/(?P<nom>.*)/(?P<prenom>.*)$', 'supprimer_organisateur_vrai'),


    url(r'^changer_mdp_organisateur$', 'changer_mdp_organisateur'),
    url(r'^lire_permission$', 'lire_permission'),
    url(r'^modifier_permission/(?P<organisateur>.*)$', 'modifier_permission'),
    url(r'^mdp_admin$', 'mdp_admin'),
    url(r'^modifier_tournoi/(?P<tournoi_lieu>.*)$', 'modifier_tournoi'),
    url(r'^lire_equipe/(?P<equipe>.*)$', 'lire_equipe'),
    url(r'^lire_eleve/(?P<equipe>.*)/(?P<indice>.*)$', 'lire_eleve'),
    url(r'^lire_encadrant/(?P<equipe>.*)/(?P<indice>.*)$', 'lire_encadrant'),
    url(r'^modifier_equipe/(?P<equipe>.*)$', 'modifier_equipe'),
    url(r'^supprimer_equipe/(?P<equipe>.*)$', 'supprimer_equipe'),
    url(r'^supprimer_equipe_vrai/(?P<equipe>.*)$', 'supprimer_equipe_vrai'),
    url(r'^modifier_eleve/(?P<equipe>.*)/(?P<indice>.*)$', 'modifier_eleve'),
    url(r'^modifier_encadrant/(?P<equipe>.*)/(?P<indice>.*)$', 'modifier_encadrant'),
    url(r'^modifier_autorisation_eleve/(?P<equipe>.*)/(?P<indice>.*)$', 'modifier_autorisation_eleve'),
	url(r'^modifier_probleme/(?P<equipe>.*)$', 'modifier_probleme'),

   	url(r'^modifier_profil_organisateur$', 'modifier_profil_organisateur'),
   	url(r'^inscription$', 'inscription_equipe'),
   	url(r'^mdp_connexion$', 'mdp_connexion'),

    url(r'^modifier_mdp_orga$', 'modifier_mdp_orga'),


   	url(r'^exportation$', 'exportation'),
	url(r'^exportation_tournoi/(?P<tournoi>.*)$', 'exportation_tournoi'),
   	url(r'^exportation_equipe/(?P<equipe>.*)$', 'exportation_equipe'),
   	url(r'^exportation_eleve/(?P<tournoi_lieu>.*)$', 'exportation_eleve'),
   	url(r'^exportation_encadrant/(?P<tournoi_lieu>.*)$', 'exportation_encadrant'),
	url(r'^log$', 'log'),
	url(r'^log_export$', 'log_export'),
	url(r'^zip_problemes/(?P<equipe>.*)$', 'zip_problemes'),
	url(r'^zip_autorisations/(?P<equipe>.*)$', 'zip_autorisations'),

  url(r'^ddl_probleme/(?P<equipe>.*)/(?P<numero>.*)/(?P<version>.*)$', 'ddl_probleme'),
  url(r'^ddl_autorisation_parentale/(?P<equipe>.*)/(?P<indice>.*)$', 'ddl_autorisation_parentale'),
  url(r'^ddl_fiche_sanitaire/(?P<equipe>.*)/(?P<indice>.*)$', 'ddl_fiche_sanitaire'),
  url(r'^ddl_autorisation_photo/(?P<equipe>.*)/(?P<indice>.*)$', 'ddl_autorisation_photo'),


	url(r'^paiement$', 'paiement'),
	url(r'^paiement_tournoi/(?P<tournoi>.*)$', 'paiement_tournoi'),
	url(r'^paiement_equipe/(?P<equipe>.*)$', 'paiement_equipe'),
	url(r'^paiement_eleve/(?P<equipe>.*)/(?P<indice>.*)$', 'paiement_eleve'),

   	url(r'^validation$', 'validation'),
   	url(r'^validation_tournoi/(?P<tournoi_lieu>.*)$', 'validation_tournoi'),
   	url(r'^validation_equipe/(?P<equipe>.*)$', 'validation_equipe'),
   	url(r'^moncompte$', 'mon_compte'),
    url(r'^confirm/(?P<code_donnee>.*)/(?P<username>.*)$', 'confirm'),
	url(r'^problemes$', 'problemes'),


	url(r'^monequipe$', 'mon_equipe'),


	url(r'^eleve/(?P<indice>.*)$', 'eleve'),
	url(r'^encadrant/(?P<indice>.*)$', 'encadrant'),
	url(r'^autorisations/(?P<indice>.*)$', 'autorisations'),



	url(r'^programme$', 'programme'),
    url(r'^tournoi_information$', 'tournoi_information'),
    url(r'^tournoi_documents','tournoi_documents'),
    url(r'^faq$', 'faq'),
    url(r'^jury$', 'jury'),

    url(r'^liste_des_problemes$', 'liste_des_problemes'),

	url(r'^editions_precedentes_participants$', 'editions_precedentes_participants'),
	url(r'^editions_precedentes_resultats$', 'editions_precedentes_resultats'),
	url(r'^editions_precedentes_solutions$', 'editions_precedentes_solutions'),
	url(r'^editions_precedentes_photos_et_videos$','editions_precedentes_photos_et_videos'),

	url(r'^temoignages$', 'temoignages'),

	url(r'^contact$', 'contact'),

	url(r'^soutenir_partenaires$', 'soutenir_partenaires'),
	url(r'^soutenir_partenaires_2014$', 'soutenir_partenaires_2014'),
	url(r'^soutenir_comment$', 'soutenir_comment'),

	url(r'^presse$', 'presse'),

	url(r'^contact$', 'itym'),

	url(r'^concours_photo$', 'concours_photo'),


)
