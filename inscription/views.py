# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required

from inscription.models import *
from inscription.forms import *
from inscription.admin import *

from random import *

import xlsxwriter

from mail_templated import send_mail
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.forms.formsets import formset_factory

from StringIO import StringIO
from zipfile import ZipFile

from django.http import StreamingHttpResponse

import os
import zipfile
import StringIO
import shutil

from datetime import *

import urllib
import httplib


from django.core.files.storage import default_storage


AWS_STORAGE_BUCKET_NAME = 'tfjm2-inscriptions'
AWS_S3_CUSTOM_DOMAIN = 's3-eu-west-1.amazonaws.com/%s' % AWS_STORAGE_BUCKET_NAME


MEDIAFILES_LOCATION = 'media'
MEDIA_URL = "http://%s/%s/" % (MEDIAFILES_LOCATION, AWS_S3_CUSTOM_DOMAIN)

BASE_DIR = "http://%s/" % AWS_S3_CUSTOM_DOMAIN





EMAIL_ENVOI = 'no-reply@tfjm.org'

LINK_SITE = "http://tfjm2-inscription.herokuapp.com"

def home(request):
    deja = 0
    users = User.objects.all()
    for p in users:
        if p.username == 'admin':
            user = User.objects.get(username='admin')
            content_type = ContentType.objects.get_for_model(Organisateur)
            permission = Permission.objects.get(content_type=content_type, codename='admin')
            permission_ecriture = "inscription.admin"
            if user.has_perm(permission_ecriture) == False:
                user.user_permissions.add(permission)
                user.save()

    return render(request,'inscription/home.html')

def liste_des_tournois(request):
    tournois = Tournoi.objects.order_by('dates')
    return render(request,'inscription/liste_des_tournois.html',locals())

def tournoi(request,lieu):
    tournois = Tournoi.objects.all()
    tournoi = Tournoi.objects.get(lieu=lieu)
    participants = Equipe.objects.filter(tournoi__lieu =lieu)

    return render(request,'inscription/tournoi.html',locals())

def tournoi_connecte(request,lieu):
    ecriture = 0
    lecture = 0
    tournois = Tournoi.objects.all()
    tournoi = Tournoi.objects.get(lieu=lieu)
    participants = Equipe.objects.filter(tournoi__lieu =lieu)
    permission_lecture = 'inscription.lecture_' + lieu
    permission_ecriture = 'inscription.ecriture_' + lieu
    if request.user.has_perm(permission_ecriture):
        ecriture = 1
    elif request.user.has_perm(permission_lecture):
        lecture = 1
    return render(request,'inscription/tournoi_connecte.html',locals())

def connexion(request):
    error = False
    mauvais_uti = 2
    mauvais_pwd = 0

    if request.method == "POST":
        form = connexion_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            for p in User.objects.all():
                if username == p.username:
                    mauvais_uti = 0
                    if p.check_password(password):
                        if p.has_perm("inscription.admin"):
                            user = authenticate(username=username, password=password)
                            login(request,user)
                            log = Log()
                            log.user = username
                            log.timestamp = datetime.now()
                            log.action =  username + u" s'est connecté."
                            log.save()
                            return redirect(home)

                        elif p.has_perm("inscription.organisateur"):
                            organisateur = Organisateur.objects.get(user__username  = p.username)
                            if organisateur.connexion == '1':
                                request.session['temp_data'] = username
                                return redirect(changer_mdp_organisateur)
                            else:
                                user = authenticate(username=username, password=password)
                                login(request,user)
                                log = Log()
                                log.user = username
                                log.timestamp = datetime.now()
                                log.action = username + u" s'est connecté."
                                log.save()
                                return redirect(home)

                        else:
                            user = authenticate(username=username, password=password)
                            login(request,user)
                            log = Log()
                            log.user = username
                            log.timestamp = datetime.now()
                            log.action = username + u" s'est connecté."
                            log.save()
                            return redirect(home)
                    else:
                        mauvais_pwd = 1
                else:
                    if mauvais_uti != 0:
                        mauvais_uti = 1    
        else:
            error = True

    else:
        form = connexion_form()

    return render(request, 'inscription/connexion.html', locals())


def mdp_oublie(request):
    error = 0
    envoi = False
    trouve = 4
    equipe_trouve = 0
    orga_trouve = 0
    if request.method == "POST":
        form = mdp_form(request.POST)
        if form.is_valid():
            trouve = 0
            for p in User.objects.all():
                if p.username == form.cleaned_data["username"]:
                    trouve = 1
                    if p.email == form.cleaned_data["email"]:

                        equipes = Equipe.objects.all()
                        for p in equipes:
                            if p.user.username == form.cleaned_data["username"]:
                                equipe_trouve = 1

                        organisateurs = Organisateur.objects.all()
                        for p in organisateurs:
                            if p.user.username == form.cleaned_data["username"]:
                                orga_trouve = 1

                        if equipe_trouve:

                            equipe = Equipe.objects.get(user__username  = form.cleaned_data["username"])
                            alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                            equipe.code_donnee = ''.join(choice(alphabet) for i in range(16))
                            equipe.save()

                            link = LINK_SITE + "/mdp/" + str(equipe.code_donnee) + "/" + equipe.user.username

                            plaintext = get_template('inscription/mdp.txt')
                            htmly     = get_template('inscription/mdp.html')

                            d = Context({
                            'username': equipe.user.username,
                            'link': link,})

                            subject, from_email, to = 'TFJM 2 - Mot de passe - Reset', EMAIL_ENVOI, equipe.user.email
                            text_content = plaintext.render(d)
                            html_content = htmly.render(d)
                            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                            msg.attach_alternative(html_content, "text/html")

                            msg.send()

                        elif orga_trouve:

                            organisateur = Organisateur.objects.get(user__username  = form.cleaned_data["username"])
                            alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                            organisateur.code_donnee = ''.join(choice(alphabet) for i in range(16))
                            organisateur.save()

                            link = LINK_SITE + "/mdp/" + str(organisateur.code_donnee) + "/" + organisateur.user.username

                            plaintext = get_template('inscription/mdp.txt')
                            htmly     = get_template('inscription/mdp.html')

                            d = Context({
                            'username': organisateur.user.last_name,
                            'link': link,})

                            subject, from_email, to = 'TFJM 2 - Mot de passe - Reset', EMAIL_ENVOI, organisateur.user.email
                            text_content = plaintext.render(d)
                            html_content = htmly.render(d)
                            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                            msg.attach_alternative(html_content, "text/html")

                            msg.send()
                        envoi = True
                    else:
                        error = 1
        else:
            error = 2
    else:
        form = mdp_form()


    if trouve==0:
        error = 3

    return render(request, 'inscription/mdp_oublie.html', locals())

def mdp(request,code_donnee,username):

    equipe_trouve = 0
    equipes = Equipe.objects.all()
    for p in equipes:
        if p.user.username == username:
            equipe_trouve = 1

    orga_trouve = 0
    organisateurs = Organisateur.objects.all()
    for p in organisateurs:
        if p.user.username == username:
            orga_trouve = 1

    if equipe_trouve:
        equipe = Equipe.objects.get(user__username  = username)

    elif orga_trouve:
        organisateur = Organisateur.objects.get(user__username  = username)

    else:
        raise Http404

    error = 0
    mdp_court=0

    if equipe_trouve:
        if equipe.code_donnee == code_donnee:

            if request.method == "POST":
                form = nouveau_mdp_form(request.POST)
                if form.is_valid():
                    if len(form.cleaned_data["password"])<8:
                        mdp_court=1
                    if form.cleaned_data["password"]==form.cleaned_data["password_conf"] and mdp_court==0:
                        equipe.user.set_password(form.cleaned_data["password"])
                        equipe.user.save()
                        equipe.save()

                        envoi = True
                    else:
                        error = 2
            else:
                form = nouveau_mdp_form()

            return render(request, 'inscription/mdp_oublie_bis.html', locals())

        else:
            raise Http404

    elif orga_trouve:
        if organisateur.code_donnee == code_donnee:

            if request.method == "POST":
                form = nouveau_mdp_form(request.POST)
                if form.is_valid():
                    if len(form.cleaned_data["password"])<8:
                        mdp_court=1
                    if form.cleaned_data["password"]==form.cleaned_data["password_conf"] and mdp_court==0:
                        organisateur.user.set_password(form.cleaned_data["password"])
                        organisateur.user.save()
                        organisateur.save()

                        envoi = True
                    else:
                        error = 2
            else:
                form = nouveau_mdp_form()

            return render(request, 'inscription/mdp_oublie_bis.html', locals())

        else:
            raise Http404



@login_required
def deconnexion(request):
    logout(request)
    return redirect(home)

@login_required
@permission_required('inscription.admin')
def ajouter_tournoi(request):
    error = False
    envoi = False
    tournoi_deja_cree = 0
    nombre_probleme = 0
    difference = 0
    difference_limite = 0
    difference_limite_def = 0
    ancien = 0
    tournois = Tournoi.objects.all()
    mtn = datetime.now()

    if request.method == "POST":
        form = ajouter_tournoi_form(request.POST)
        if form.is_valid():
            tournois = Tournoi.objects.all()
            for p in tournois:
                if p.lieu == form.cleaned_data["lieu"]:
                    tournoi_deja_cree = 1
            nb = "0123456789"
            for p in form.cleaned_data["nombre_problemes"]:
                if p not in nb:
                    nombre_probleme = 1
            tournoi = Tournoi()
            tournoi.dates = form.cleaned_data["dates"]
            tournoi.dates_fin = form.cleaned_data["dates_fin"]
            tournoi.date_limite = form.cleaned_data["date_limite"]
            tournoi.date_limite_def = form.cleaned_data["date_limite_def"]

            if tournoi.dates_fin < tournoi.dates:
                difference = 1

            if tournoi.date_limite > tournoi.dates:
                difference_limite = 1

            if tournoi.date_limite_def > tournoi.dates:
                difference_limite_def = 1

            if tournoi.dates < mtn.date() or tournoi.dates_fin < mtn.date():
                ancien = 1


            if tournoi_deja_cree == 0 and nombre_probleme == 0 and difference == 0 and difference_limite == 0 and difference_limite_def == 0 and ancien == 0:
                tournoi = Tournoi()
                tournoi.lieu = form.cleaned_data["lieu"]
                tournoi.dates = form.cleaned_data["dates"]
                tournoi.dates_fin = form.cleaned_data["dates_fin"]
                tournoi.description = form.cleaned_data["description"]
                tournoi.nombre_problemes = form.cleaned_data["nombre_problemes"]
                tournoi.date_limite = form.cleaned_data["date_limite"]
                tournoi.date_limite_def = form.cleaned_data["date_limite_def"]
                tournoi.organisateurs = form.cleaned_data["organisateurs"]
                tournoi.nombre_equipes_validees_max = form.cleaned_data["nombre_equipes_validees_max"]

                content_type = ContentType.objects.get_for_model(Tournoi)

                Permission.objects.create(
                codename= 'lecture_' + tournoi.lieu ,
                name= 'Droit de LECTURE sur le tournoi de ' + tournoi.lieu,
                content_type=content_type)

                Permission.objects.create(
                codename= 'ecriture_' + tournoi.lieu ,
                name= 'Droit de ECRITURE sur le tournoi de ' + tournoi.lieu,
                content_type=content_type)

                Permission.objects.create(
                codename= 'paiement_' + tournoi.lieu ,
                name= 'Droit de PAIEMENT sur le tournoi de ' + tournoi.lieu,
                content_type=content_type)

                tournoi.save()

                log = Log()
                log.user = request.user.username
                log.timestamp = datetime.now()
                log.action = request.user.username + u" a ajouté un tournoi: " + tournoi.lieu
                log.save()

                envoi = True

        else:
            error = True
    else:
        form = ajouter_tournoi_form()

    return render(request,'inscription/ajouter_tournoi.html', locals())
# règles de validation des dates et du lieu (majuscule)



@login_required
@permission_required('inscription.admin')

def ajouter_organisateur(request):
    organisateurs = Organisateur.objects.all()
    error = False
    envoi = False
    organisateur_deja_cree = 0

    if request.method == "POST":
        form = ajouter_organisateur_form(request.POST)
        if form.is_valid():
            organisateurs = Organisateur.objects.all()
            for p in organisateurs:
                if p.user.username == form.cleaned_data["username"]or p.user.email == form.cleaned_data["email"] :
                    organisateur_deja_cree = 1


            for p in User.objects.all():
                if p.username == form.cleaned_data["username"]or p.email == form.cleaned_data["email"]:
                    organisateur_deja_cree = 1

            if organisateur_deja_cree == 0:
                organisateur = Organisateur()
                alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                mdp = ''.join(choice(alphabet) for i in range(10))
                user = User.objects.create_user(username = form.cleaned_data["username"], email = form.cleaned_data["email"],
                        password = mdp, first_name = form.cleaned_data["prenom"], last_name = form.cleaned_data["nom"])
                organisateur.user = user

                content_type = ContentType.objects.get_for_model(Organisateur)
                permission = Permission.objects.get(content_type=content_type, codename='organisateur')
                user.user_permissions.add(permission)
                
                plaintext = get_template('inscription/email_nouveau_organisateur.txt')
                htmly     = get_template('inscription/email_nouveau_organisateur.html')

                d = Context({
                                        'nom': organisateur.user.last_name,
                                        'prenom': organisateur.user.first_name,
                                        'username': organisateur.user.username,
                                        'password': mdp,})

                subject, from_email, to = 'TFJM 2 - Organisateur', EMAIL_ENVOI, organisateur.user.email
                text_content = plaintext.render(d)
                html_content = htmly.render(d)
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")



                msg.send()
                user.save()
                organisateur.save()
                log = Log()
                log.user = request.user.username
                log.timestamp = datetime.now()
                log.action = request.user.username + u" a créé le compte organisateur " + user.username
                log.save()
                orga = organisateur.user.last_name +" "+ organisateur.user.first_name
                return redirect(modifier_permission, organisateur=orga )

                envoi = True
        else:
            error = True
    else:
        form = ajouter_organisateur_form()

    return render(request,'inscription/ajouter_organisateur.html', locals())


#mail admin provenance
#mettre le lien de connexion dans le mail



@login_required
@permission_required('inscription.admin')


def supprimer_organisateur(request,nom,prenom):

    organisateur = Organisateur.objects.get(user__last_name  = nom, user__first_name  = prenom)
    confirmation = False
    
    if request.method == "POST":
        confirmation = True
    else:
        form1 = supprimer1_organisateur_form()

    return render(request,'inscription/supprimer_organisateur.html', locals())


@login_required
@permission_required('inscription.admin')

def supprimer_organisateur_vrai(request,nom,prenom):

    organisateur = Organisateur.objects.get(user__last_name  = nom, user__first_name  = prenom)
    organisateur.user.is_active = False
    organisateur.user.save()
    organisateur.save()

    return redirect(liste_organisateur)


@login_required
@permission_required('inscription.admin')

def lire_permission(request):
    organisateurs = Organisateur.objects.all() #exclure admin?
    tournois = Tournoi.objects.all()
    permissions = {}
    for org in organisateurs:
        dico = {}
        for tr in tournois:
            permission_ecriture = "inscription.ecriture_" + tr.lieu
            permission_lecture = "inscription.lecture_" + tr.lieu
            permission_paiement = "inscription.paiement_" + tr.lieu

            if org.user.has_perm(permission_ecriture):
                dico[tr.lieu] =  "Ecriture"
            elif org.user.has_perm(permission_lecture):
                dico[tr.lieu] = "Lecture"
            else:
                dico[tr.lieu] = "Aucune"

            if org.user.has_perm(permission_paiement):
                dico[tr.lieu] = dico[tr.lieu] + " + Paiement"

        name = org.user.last_name + " " + org.user.first_name
        permissions[name] = dico

    return render(request,'inscription/lire_permission.html', locals())



@login_required
@permission_required('inscription.admin')

def modifier_permission(request, organisateur):
    
    espaces = 0
    for p in organisateur:
        if p == ' ':
            espaces += 1

    if espaces == 2:
        organisateur = organisateur.split(' ', 2 )
    elif espaces == 1:
        organisateur = organisateur.split(' ', 1 )
 

    numb = 0    
    for p in organisateur:
        if numb<1:
            orga_bis = p
            numb = 1
        else:
            orga = p



    modifier_permission_form_set = formset_factory(modifier_permission_form)

    org = Organisateur.objects.get(user__last_name  = orga_bis, user__first_name  = orga, )

    tournois = Tournoi.objects.all()

    data_sample_org = {
     'form-TOTAL_FORMS': '10',
     'form-INITIAL_FORMS': '0',
     'form-MAX_NUM_FORMS': '',
            }

    compteur = 0

    for tr in tournois:
        permission_lecture = "inscription.lecture_" + tr.lieu
        permission_ecriture = "inscription.ecriture_" + tr.lieu
        permission_paiement = "inscription.paiement_" + tr.lieu
        formulaire = "form-"+str(compteur)+"-permission"
        if org.user.has_perm(permission_lecture):
            data_sample_org[formulaire] = '1'
        elif org.user.has_perm(permission_ecriture):
            data_sample_org[formulaire] = '2'
        else:
            data_sample_org[formulaire] = '3'

        formulaire = "form-"+str(compteur)+"-permission_paiement"

        if org.user.has_perm(permission_paiement):
            data_sample_org[formulaire] = '1'
        else:
            data_sample_org[formulaire] = '2'

        compteur+=1

    if request.method == 'POST':
        formset = modifier_permission_form_set(request.POST)
        if formset.is_valid():
            for tr,form in zip(tournois,formset):
                permission_ecriture1 = "inscription.ecriture_" + tr.lieu
                permission_lecture1 = "inscription.lecture_" + tr.lieu
                permission_paiement1 = "inscription.paiement_" + tr.lieu

                content_type = ContentType.objects.get_for_model(Tournoi)
                lecture = "lecture_" + tr.lieu
                permission_lecture2 = Permission.objects.get(content_type=content_type, codename=lecture)

                content_type = ContentType.objects.get_for_model(Tournoi)
                ecriture = "ecriture_" + tr.lieu
                permission_ecriture2 = Permission.objects.get(content_type=content_type, codename=ecriture)

                content_type = ContentType.objects.get_for_model(Tournoi)
                paiement = "paiement_" + tr.lieu
                permission_paiement2 = Permission.objects.get(content_type=content_type, codename=paiement)

                if org.user.has_perm(permission_lecture1):
                    if form.cleaned_data["permission"] == '2':
                        org.user.user_permissions.remove(permission_lecture2)
                        org.user.user_permissions.add(permission_ecriture2)
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié une permission à " + org.user.username + ": " + permission_lecture2.name + " >>> " + permission_ecriture2.name + "."
                        log.save()
                    elif form.cleaned_data["permission"] == '3':
                        org.user.user_permissions.remove(permission_lecture2)
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a enlevé une permission à " + org.user.username + ": " + permission_lecture2.name  + "."
                        log.save()
                elif org.user.has_perm(permission_ecriture1):
                    if form.cleaned_data["permission"] =='1':
                        org.user.user_permissions.remove(permission_ecriture2)
                        org.user.user_permissions.add(permission_lecture2)
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié une permission à " + org.user.username + ": " + permission_ecriture2.name + " >>> " + permission_lecture2.name + "."
                        log.save()
                    elif form.cleaned_data["permission"] == '3':
                        org.user.user_permissions.remove(permission_ecriture2)
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a enlevé une permission à " + org.user.username + ": " + permission_ecriture2.name + "."
                        log.save()
                else:
                    if form.cleaned_data["permission"] == '1':
                            org.user.user_permissions.add(permission_lecture2)
                            log = Log()
                            log.user = request.user.username
                            log.timestamp = datetime.now()
                            log.action = request.user.username + u" a ajouté une permission à " + org.user.username + ": " + permission_lecture2.name + "."
                            log.save()
                    elif form.cleaned_data["permission"] == '2':
                            org.user.user_permissions.add(permission_ecriture2)
                            log = Log()
                            log.user = request.user.username
                            log.timestamp = datetime.now()
                            log.action = request.user.username + u" a ajouté une permission de " + org.user.username + ": " + permission_ecriture2.name + "."
                            log.save()


                if org.user.has_perm(permission_paiement1):
                    if form.cleaned_data["permission_paiement"] == '2':
                        org.user.user_permissions.remove(permission_paiement2)
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a enlevé une permission à " + org.user.username + ": " + permission_paiement2.name + "."
                        log.save()
                else:
                    if form.cleaned_data["permission_paiement"] == '1':
                        org.user.user_permissions.add(permission_paiement2)
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a ajouté une permission à " + org.user.username + ": " + permission_paiement2.name + "."
                        log.save()

                envoi = True

    else:
        formset = modifier_permission_form_set(data_sample_org)

    liste = {}
    for tr,form in zip(tournois,formset):
        liste[tr.lieu] = form

    return render(request,'inscription/modifier_permission.html', locals())

#lecture, écriture, paiement, rien




@login_required
@permission_required('inscription.admin')
def mdp_admin(request):
    mdp_court=0
    if request.method == "POST":
        form = changer_mdp_admin_form(request.POST)
        if form.is_valid():
            if len(form.cleaned_data["password"])<8:
                mdp_court=1
            if form.cleaned_data["password"] == form.cleaned_data["password_conf"] and mdp_court==0:
                logout(request)
                user = User.objects.get(username = "admin")
                user.set_password(form.cleaned_data["password"])
                user.save()
                envoi = True
            else:
                error = True

        else:
            error = True
    else:
        form = changer_mdp_admin_form()

    return render(request,'inscription/mdp_admin.html', locals())


@login_required
@permission_required('inscription.admin')
def log(request):

    delta = date.today() - timedelta(days=10)
    log = Log.objects.filter(timestamp__year = delta.year, timestamp__month = delta.month)

    return render(request,'inscription/log.html', locals())


@login_required
@permission_required('inscription.admin')
def log_export(request):
    queryset = Log.objects.all()
    dataset = LogResource().export(queryset)
    my_data = dataset.xls
    filename = "log.xls"
    response = HttpResponse(my_data, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response








@login_required
def liste_organisateur(request):
    if request.user.has_perm('inscription.organisateur') or request.user.has_perm('inscription.admin'):
        organisateurs = Organisateur.objects.filter(user__is_active = True)
        return render(request,'inscription/liste_organisateur.html', locals())
    else:
        raise Http404

@login_required
def lire_profile_organisateur(request, organisateur_last_name, organisateur_first_name):
    if request.user.has_perm('inscription.organisateur') or request.user.has_perm('inscription.admin'):
        organisateur = Organisateur.objects.get(user__last_name  = organisateur_last_name, user__first_name  = organisateur_first_name)
        organisateurs = Organisateur.objects.filter(user__is_active = True)
        return render(request,'inscription/liste_profile_organisateur.html', locals())
    else:
        raise Http404



def changer_mdp_organisateur(request):
    organisateur = Organisateur.objects.get(user__username  = request.session['temp_data'])
    error = False
    envoi = False
    mdp_court=0
    if organisateur.user.has_perm('inscription.organisateur') and organisateur.connexion == '1':
        if request.method == "POST":
            form = changer_mdp_organisateur_form(request.POST)
            if form.is_valid():
                if len(form.cleaned_data["password"])<8:
                    mdp_court=1
                if form.cleaned_data["password"] == form.cleaned_data["password_conf"] and mdp_court==0:
                    organisateur.user.set_password(form.cleaned_data["password"])
                    organisateur.connexion = '0'
                    organisateur.user.save()
                    organisateur.save()

                    envoi = True
                else:
                    error = True

            else:
                error = True
        else:
            form = changer_mdp_organisateur_form()

        return render(request,'inscription/changer_mdp_organisateur.html', locals())
    else:
        raise Http404

#template ne mettre que le formulaire rien d'autre autour (même que l'admin autre base.html)



@login_required
def modifier_tournoi(request, tournoi_lieu):
    permission = 'inscription.ecriture_' + tournoi_lieu

    if request.user.has_perm(permission):
        tournoi = Tournoi.objects.get(lieu = tournoi_lieu)
        tournois = Tournoi.objects.all()
        error = False
        envoi = False
        nombre_probleme = 0
        difference = 0
        difference_limite = 0
        difference_limite_def = 0
        ancien = 0
        tournoi_deja_cree = 0

        if request.method == "POST":
            form = modifier_tournoi_form(request.POST, instance = tournoi)
            if form.is_valid():
                nb = "0123456789"
                for p in form.cleaned_data["nombre_equipes_validees_max"]:
                    if p not in nb:
                        nombre_probleme = 1

                tournoi_essai = Tournoi()
                tournoi_essai.dates = form.cleaned_data["dates"]
                tournoi_essai.dates_fin = form.cleaned_data["dates_fin"]
                tournoi_essai.date_limite = form.cleaned_data["date_limite"]
                tournoi_essai.date_limite_def = form.cleaned_data["date_limite_def"]

                if tournoi_essai.dates_fin < tournoi_essai.dates:
                    difference = 1

                if tournoi_essai.date_limite > tournoi_essai.dates:
                    difference_limite = 1

                if tournoi_essai.date_limite_def > tournoi_essai.dates:
                    difference_limite_def = 1

                mtn = datetime.now()

                if tournoi_essai.dates < mtn.date() or tournoi_essai.dates_fin < mtn.date():
                    ancien = 1


                if tournoi_deja_cree == 0 and nombre_probleme == 0 and difference == 0 and difference_limite == 0 and difference_limite_def == 0 and ancien == 0:

                    if tournoi.dates != form.cleaned_data["dates"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié la date de début du tournoi de " + tournoi.lieu + ":" + tournoi.dates + " >>> " + form.cleaned_data["dates"]
                        log.save()
                        tournoi.dates = form.cleaned_data["dates"]

                    if tournoi.dates_fin != form.cleaned_data["dates_fin"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié les date de fin du tournoi de " + tournoi.lieu + ":" + tournoi.dates_fin + " >>> " + form.cleaned_data["dates_fin"]
                        log.save()
                        tournoi.dates_fin = form.cleaned_data["dates_fin"]

                    if tournoi.description != form.cleaned_data["description"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié la description du tournoi de " + tournoi.lieu + ":" + tournoi.description + " >>> " + form.cleaned_data["description"]
                        log.save()
                        tournoi.description = form.cleaned_data["description"]

                    if tournoi.nombre_equipes_validees_max != form.cleaned_data["nombre_equipes_validees_max"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié le nombre maximum d'équipes pour le tournoi de " + tournoi.lieu + ":" + tournoi.nombre_equipes_validees_max + " >>> " + form.cleaned_data["nombre_equipes_validees_max"]
                        log.save()
                        tournoi.nombre_equipes_validees_max = form.cleaned_data["nombre_equipes_validees_max"]

                    if tournoi.organisateurs != form.cleaned_data["organisateurs"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié les organisateurs du tournoi de " + tournoi.lieu + ":" + tournoi.organisateurs + " >>> " + form.cleaned_data["organisateurs"]
                        log.save()
                        tournoi.organisateurs = form.cleaned_data["organisateurs"]

                    if tournoi.date_limite != form.cleaned_data["date_limite"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié la date limite d'inscription du tournoi de " + tournoi.lieu + ":" + tournoi.date_limite + " >>> " + form.cleaned_data["date_limite"]
                        log.save()
                        tournoi.date_limite = form.cleaned_data["date_limite"]

                    if tournoi.date_limite_def != form.cleaned_data["date_limite_def"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié la date limite définitive d'inscription du tournoi de " + tournoi.lieu + ":" + tournoi.date_limite_def + " >>> " + form.cleaned_data["date_limite_def"]
                        log.save()
                        tournoi.date_limite_def = form.cleaned_data["date_limite_def"]

                    tournoi.save()


                    envoi = True
            else:
                error = True
        else:
            form = modifier_tournoi_form(instance = tournoi)

        return render(request,'inscription/modifier_tournoi.html', locals())
    else:
        raise Http404
# règles de validation des dates et du lieu (majuscule)


@login_required
def lire_equipe(request, equipe):
    equipe = Equipe.objects.get(nom_equipe = equipe)
    equipes = Equipe.objects.filter(tournoi__lieu  = equipe.tournoi.lieu)
    encadrants = Encadrant.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)
    eleves = Eleve.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)
    permission_lecture = 'inscription.lecture_' + equipe.tournoi.lieu
    permission_ecriture = 'inscription.ecriture_' + equipe.tournoi.lieu

    nb_max = int(equipe.tournoi.nombre_problemes) + 1


    problemes_fichier = {}

    import collections

    problemes1 = Probleme.objects.filter(equipe__nom_equipe=equipe.nom_equipe).order_by('numero')

    for p in problemes1:
        key = p.numero+"_version1"
        pbs = Probleme.objects.filter(equipe__nom_equipe=equipe.nom_equipe, numero = p.numero)
        maxi = 0
        for t in pbs:
            if int(t.version)>maxi:
                maxi = int(t.version)
        problemes_fichier[key] = Probleme.objects.get(equipe__user__username= equipe.user.username, numero = p.numero, version = str(maxi))

    od_probleme = collections.OrderedDict(sorted(problemes_fichier.items()))

    if request.user.has_perm(permission_lecture) and equipe.inscription_validee == '1':
        lecture = 1
        return render(request,'inscription/lire_equipe.html', locals())
    elif request.user.has_perm(permission_ecriture):
        ecriture = 1
        return render(request,'inscription/lire_equipe.html', locals())
    else:
        raise Http404



def zip_problemes(request,equipe):
    equipe = Equipe.objects.get(nom_equipe = equipe)
    tournoi = Tournoi.objects.get(lieu = equipe.tournoi.lieu)
    permission_lecture = 'inscription.lecture_' + tournoi.lieu
    permission_ecriture = 'inscription.ecriture_' + tournoi.lieu
    problemes = Probleme.objects.filter(equipe__nom_equipe =equipe.nom_equipe, version='1')

    if (request.user.has_perm(permission_lecture) and equipe.inscription_validee=='1') or request.user.has_perm(permission_ecriture):
        # Files (local path) to put in the .zip
        # FIXME: Change this (get paths from DB etc)
        filenames = []
        

        nb_max = int(equipe.tournoi.nombre_problemes) + 1

        problemes_fichier= {}

        for i in range(1,nb_max):
            problemes = Probleme.objects.filter(equipe__nom_equipe  = equipe.nom_equipe, numero = i)
            max = -1
            for p in problemes:
                if int(p.version) > max:
                    max = int(p.version)

            problemes = Probleme.objects.get(equipe__nom_equipe  = equipe.nom_equipe, numero = i, version = str(max))

            problemes_fichier[i] = problemes



        os.mkdir("/app/probleme")
        os.chdir("/app/probleme")

        for key,p in problemes_fichier.items():
            url = p.fichier.url

            if p.version == '1' or p.version =='2':
                p.version = '0'
            else:
                p.version = str(int(p.version) - 2)

            if equipe.trigramme != 'T':
                name = equipe.trigramme + "_probleme" + p.numero + "_version" + p.version
            else:
                name = "probleme" + p.numero + "_version" + p.version + ".pdf"
            
            urllib.urlretrieve(url, name)

            url = "/app/probleme/" + name

            filenames.append(url)

        # Folder name in ZIP archive which contains the above files
        # E.g [thearchive.zip]/somefiles/file2.txt
        # FIXME: Set this to something better
        zip_subdir = "Problemes_"+ equipe.nom_equipe
        zip_filename = "%s.zip" % zip_subdir

        # Open StringIO to grab in-memory ZIP contents
        s = StringIO.StringIO()

        # The zip compressor
        zf = zipfile.ZipFile(s, "w")

        for fpath in filenames:
            # Calculate path for file in zip
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)

            # Add file, at correct path
            zf.write(fpath, zip_path)

        # Must close zip for all contents to be written
        zf.close()

        # Grab ZIP file from in-memory, make response with correct MIME-type
        resp = HttpResponse(s.getvalue(), content_type='application/x-zip-compressed')
        # ..and correct content-disposition
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        shutil.rmtree("/app/probleme/")

        return resp
    else:
        raise Http404


def zip_autorisations(request,equipe):
    equipe = Equipe.objects.get(nom_equipe = equipe)
    tournoi = Tournoi.objects.get(lieu = equipe.tournoi.lieu)
    permission_lecture = 'inscription.lecture_' + tournoi.lieu
    permission_ecriture = 'inscription.ecriture_' + tournoi.lieu
    eleves = Eleve.objects.filter(equipe__nom_equipe =equipe.nom_equipe)

    if (request.user.has_perm(permission_lecture) and equipe.inscription_validee=='1') or request.user.has_perm(permission_ecriture):

        filenames = []
        
        os.mkdir("/app/autorisations")
        os.chdir("/app/autorisations")

        for p in eleves:

            url = p.fiche_sanitaire.url
            if equipe.trigramme != 'T':
                name = equipe.trigramme + "_fiche_sanitaire" + p.nom + ".pdf"
            else:
                name = "_fiche_sanitaire" + p.nom + ".pdf"
            urllib.urlretrieve(url, name)
            url = "/app/autorisations/" + name         
            filenames.append(url)

            url = p.autorisation_parentale.url
            if equipe.trigramme != 'T':
                name = equipe.trigramme + "_autorisation_parentale" + p.nom + ".pdf"
            else:
                name = "_autorisation_parentale" + p.nom + ".pdf"
            urllib.urlretrieve(url, name)
            url = "/app/autorisations/" + name            
            filenames.append(url)

            url = p.autorisation_photo.url
            if equipe.trigramme != 'T':
                name = equipe.trigramme + "_autorisation_photo" + p.nom + ".pdf"
            else:
                name = "_autorisation_photo" + p.nom + ".pdf"
            urllib.urlretrieve(url, name)
            url = "/app/autorisations/" + name            
            filenames.append(url)

        zip_subdir = "Autorisations_" + equipe.nom_equipe
        zip_filename = "%s.zip" % zip_subdir
        s = StringIO.StringIO()
        zf = zipfile.ZipFile(s, "w")
        for fpath in filenames:
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)
            zf.write(fpath, zip_path)

        zf.close()
        response = HttpResponse(s.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        shutil.rmtree("/app/autorisations/")
        return response
    else:
        raise Http404







@login_required
def lire_eleve(request, equipe, indice):
    equipe = Equipe.objects.get(nom_equipe = equipe)
    eleve = Eleve.objects.get(equipe = equipe, indice = indice)
    encadrants = Encadrant.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)
    eleves = Eleve.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)
    permission_lecture = 'inscription.lecture_' + equipe.tournoi.lieu
    permission_ecriture = 'inscription.ecriture_' + equipe.tournoi.lieu

    if request.user.has_perm(permission_lecture) and equipe.inscription_validee == '1' :
        return render(request,'inscription/lire_eleve.html', locals())
    elif request.user.has_perm(permission_ecriture):
        ecriture = 1
        return render(request,'inscription/lire_eleve.html', locals())
    else:
        raise Http404


@login_required
def lire_encadrant(request, equipe, indice):
    equipe = Equipe.objects.get(nom_equipe = equipe)
    encadrant = Encadrant.objects.get(equipe = equipe, indice = indice)
    encadrants = Encadrant.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)
    eleves = Eleve.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)
    permission_lecture = 'inscription.lecture_' + equipe.tournoi.lieu
    permission_ecriture = 'inscription.ecriture_' + equipe.tournoi.lieu

    if request.user.has_perm(permission_lecture) and equipe.inscription_validee == '1':
        return render(request,'inscription/lire_encadrant.html', locals())
    elif request.user.has_perm(permission_ecriture):
        ecriture = 1
        return render(request,'inscription/lire_encadrant.html', locals())
    else:
        raise Http404



@login_required
def modifier_equipe(request, equipe):
    equipe = Equipe.objects.get(nom_equipe = equipe)
    permission = 'inscription.ecriture_' + equipe.tournoi.lieu
    equipes = Equipe.objects.filter(tournoi__lieu  = equipe.tournoi.lieu)


    if request.user.has_perm(permission):
        if request.method == "POST":
            form = Equipe_Form(request.POST, instance = equipe)
            if form.is_valid():
                if equipe.tournoi != form.cleaned_data["tournoi"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié le tournoi de l'équipe " + equipe.nom_equipe + ":" + equipe.tournoi + " >>> " + form.cleaned_data["tournoi"] + "."
                    log.save()
                    equipe.tournoi = form.cleaned_data["tournoi"]

                if equipe.nombre_eleves != form.cleaned_data["nombre_eleves"]:

                    if int(form.cleaned_data["nombre_eleves"]) > int(equipe.nombre_eleves):
                        for p in range(int(form.cleaned_data["nombre_eleves"]) - int(equipe.nombre_eleves)):
                            eleve = Eleve()
                            eleve.indice = str(int(equipe.nombre_eleves)+p+1)
                            eleve.equipe = equipe
                            eleve.nom = "Eleve" + str(int(equipe.nombre_eleves)+p+1)
                            eleve.save()
                    elif int(form.cleaned_data["nombre_eleves"]) < int(equipe.nombre_eleves):
                        for p in range(int(form.cleaned_data["nombre_eleves"]), int(equipe.nombre_eleves)):
                            eleve = Eleve.objects.get(indice = str(p + 1), equipe = equipe)
                            eleve.delete()

                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié son nombre d'élèves:" + equipe.nombre_eleves +  " >>> " + form.cleaned_data["nombre_eleves"] + "."
                    log.save()

                    equipe.nombre_eleves = form.cleaned_data["nombre_eleves"]


                if equipe.nombre_encadrants != form.cleaned_data["nombre_encadrants"]:

                    if int(form.cleaned_data["nombre_encadrants"]) > int(equipe.nombre_encadrants):
                        for p in range(int(form.cleaned_data["nombre_encadrants"]) - int(equipe.nombre_encadrants)):
                            encadrant = Encadrant()
                            encadrant.indice = str(int(equipe.nombre_encadrants)+p+1)
                            encadrant.equipe = equipe
                            encadrant.nom = "Encadrant" + str(int(equipe.nombre_encadrants)+p+1)
                            encadrant.save()
                    elif int(form.cleaned_data["nombre_encadrants"]) < int(equipe.nombre_encadrants):
                        for p in range(int(form.cleaned_data["nombre_encadrants"]), int(equipe.nombre_encadrants)):
                            encadrant = Encadrant.objects.get(indice = str(p + 1), equipe = equipe)
                            encadrant.delete()

                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié son nombre d'encadrants:" + equipe.nombre_encadrants +  " >>> " + form.cleaned_data["nombre_encadrants"] + "."
                    log.save()

                    equipe.nombre_encadrants = form.cleaned_data["nombre_encadrants"]
                    

                equipe.save()

                envoi = True
            else:
                error = True
        else:
            form = Equipe_Form(instance = equipe)
        return render(request,'inscription/modifier_equipe.html', locals())
    else:
        raise Http404
#  a completer avec toutes les case d'une equipe (form y compris)



@login_required
def supprimer_equipe(request, equipe):
    equipe = Equipe.objects.get(nom_equipe = equipe)
    permission = 'inscription.ecriture_' + equipe.tournoi.lieu
    confirmation = False

    if request.user.has_perm(permission) and (equipe.inscription_validee != '1'):
        if request.method == "POST":
            confirmation = True
        else:
            form1 = supprimer1_equipe_form()

        return render(request,'inscription/supprimer_equipe.html', locals())
    else:
        raise Http404

@login_required
def supprimer_equipe_vrai(request, equipe):

    eleves = Eleve.objects.filter(equipe__nom_equipe = equipe)
    for p in eleves:
        p.delete()

    encadrants = Encadrant.objects.filter(equipe__nom_equipe = equipe)
    for p in encadrants:
        p.delete()

    problemes = Probleme.objects.filter(equipe__nom_equipe = equipe)
    for p in problemes:
        p.delete

    log = Log()
    log.user = request.user.username
    log.timestamp = datetime.now()
    log.action = request.user.username + u" a supprimé l'équipe " + equipe + "."
    log.save()

    equipe = Equipe.objects.get(nom_equipe = equipe)
    tr = equipe.tournoi.lieu
    equipe.user.delete()
    equipe.delete()

    return redirect(tournoi_connecte, lieu=tr)


@login_required
def modifier_eleve(request, equipe, indice):
    equipe = Equipe.objects.get(nom_equipe = equipe)
    encadrants = Encadrant.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)
    eleves = Eleve.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)
    permission = 'inscription.ecriture_' + equipe.tournoi.lieu
    eleve = Eleve.objects.get(indice = indice, equipe = equipe)
    naissance_probleme = 0
    code_postale_probleme = 0
    nombre_code_postale_probleme = 0

    if request.user.has_perm(permission):
        if request.method == "POST":
            form = Inscription_Eleve(request.POST, instance = eleve)
            if form.is_valid():

                now = datetime.now().date()
                op = Eleve()
                op.date_naissance = form.cleaned_data["date_naissance"]

                if op.date_naissance:
                    if op.date_naissance > now:
                        naissance_probleme = 1

                nb = "0123456789"
                for p in form.cleaned_data["code_postale"]:
                    if p not in nb:
                        code_postale_probleme = 1

                compteur = 0
                for p in form.cleaned_data["code_postale"]:
                    compteur +=1
                if compteur != 5:
                    nombre_code_postale_probleme = 1


                if naissance_probleme == 0 and nombre_code_postale_probleme == 0 and code_postale_probleme == 0:
                    if eleve.nom != form.cleaned_data["nom"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié le nom de l'élève " + eleve.nom + ":" + eleve.nom + " >>> " + form.cleaned_data["nom"] + "."
                        log.save()
                        eleve.nom = form.cleaned_data["nom"]

                    if eleve.prenom != form.cleaned_data["prenom"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié le prénom de l'élève " + eleve.nom + ":" + eleve.prenom + " >>> " + form.cleaned_data["prenom"] + "."
                        log.save()
                        eleve.prenom = form.cleaned_data["prenom"]

                    if eleve.nom != form.cleaned_data["sexe"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié le sexe de l'élève " + eleve.nom + ":" + eleve.sexe + " >>> " + form.cleaned_data["sexe"] + "."
                        log.save()
                        eleve.sexe = form.cleaned_data["sexe"]

                    if eleve.email != form.cleaned_data["email"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié l'email de l'élève " + eleve.nom + ":" + eleve.email + " >>> " + form.cleaned_data["email"] + "."
                        log.save()
                        eleve.email = form.cleaned_data["email"]

                    if eleve.date_naissance != form.cleaned_data["date_naissance"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié la date de naissance de l'élève " + eleve.nom + ":" + eleve.date_naissance + " >>> " + form.cleaned_data["date_naissance"] + "."
                        log.save()
                        eleve.date_naissance = form.cleaned_data["date_naissance"]

                    if eleve.nom_etablissement != form.cleaned_data["nom_etablissement"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié le nom de l'établissement de l'élève " + eleve.nom + ":" + eleve.nom_etablissement + " >>> " + form.cleaned_data["nom_etablissement"] + "."
                        log.save()
                        eleve.nom_etablissement = form.cleaned_data["nom_etablissement"]

                    if eleve.ville_etablissement != form.cleaned_data["ville_etablissement"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié la ville de l'établissement de l'élève " + eleve.nom + ":" + eleve.ville_etablissement + " >>> " + form.cleaned_data["ville_etablissement"] + "."
                        log.save()
                        eleve.ville_etablissement = form.cleaned_data["ville_etablissement"]

                    if eleve.classe != form.cleaned_data["classe"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié la classe de l'élève " + eleve.nom + ":" + eleve.classe + " >>> " + form.cleaned_data["classe"] + "."
                        log.save()
                        eleve.classe = form.cleaned_data["classe"]

                    if eleve.adresse != form.cleaned_data["adresse"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié l'adresse de l'élève " + eleve.nom + ":" + eleve.adresse + " >>> " + form.cleaned_data["adresse"] + "."
                        log.save()
                        eleve.adresse = form.cleaned_data["adresse"]

                    if eleve.code_postale != form.cleaned_data["code_postale"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié le code postale de l'élève " + eleve.nom + ":" + eleve.code_postale + " >>> " + form.cleaned_data["code_postale"] + "."
                        log.save()
                        eleve.code_postale = form.cleaned_data["code_postale"]

                    if eleve.nom_responsable_legal != form.cleaned_data["nom_responsable_legal"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié le nom du responsable légal de l'élève " + eleve.nom + ":" + eleve.nom_responsable_legal + " >>> " + form.cleaned_data["nom_responsable_legal"] + "."
                        log.save()
                        eleve.nom_responsable_legal = form.cleaned_data["nom_responsable_legal"]

                    if eleve.coordonnees_responsable_legal != form.cleaned_data["coordonnees_responsable_legal"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié le nom du responsable légal de l'élève " + eleve.nom + ":" + eleve.coordonnees_responsable_legal + " >>> " + form.cleaned_data["coordonnees_responsable_legal"] + "."
                        log.save()
                        eleve.coordonnees_responsable_legal = form.cleaned_data["coordonnees_responsable_legal"]

                    eleve.save()

                    envoi = True
            else:
                error = True
        else:
            form = Inscription_Eleve(instance = eleve)
        return render(request,'inscription/modifier_eleve.html', locals())
    else:
        raise Http404

#  a completer avec toutes les case d'un eleve (form y compris)


@login_required
def modifier_encadrant(request, equipe,indice):
    equipe = Equipe.objects.get(nom_equipe = equipe)
    permission = 'inscription.ecriture_' + equipe.tournoi.lieu
    encadrant = Encadrant.objects.get(indice = indice, equipe = equipe)
    encadrants = Encadrant.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)
    eleves = Eleve.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)

    if request.user.has_perm(permission):
        if request.method == "POST":
            form = Inscription_Encadrant(request.POST, instance = encadrant)
            if form.is_valid():
                if encadrant.nom != form.cleaned_data["nom"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié le nom de l'encadrant " + encadrant.nom + ":" + encadrant.nom + " >>> " + form.cleaned_data["nom"] + "."
                    log.save()
                    encadrant.nom = form.cleaned_data["nom"]

                if encadrant.prenom != form.cleaned_data["prenom"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié le prenom de l'encadrant " + encadrant.prenom + ":" + encadrant.prenom + " >>> " + form.cleaned_data["prenom"] + "."
                    log.save()
                    encadrant.prenom = form.cleaned_data["prenom"]

                if encadrant.sexe != form.cleaned_data["sexe"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié le sexe de l'encadrant " + encadrant.sexe + ":" + encadrant.sexe + " >>> " + form.cleaned_data["sexe"] + "."
                    log.save()
                    encadrant.sexe = form.cleaned_data["sexe"]

                if encadrant.email != form.cleaned_data["email"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié l'email de l'encadrant " + encadrant.email + ":" + encadrant.email + " >>> " + form.cleaned_data["email"] + "."
                    log.save()
                    encadrant.email = form.cleaned_data["email"]

                if encadrant.profession != form.cleaned_data["profession"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié la profession de l'encadrant " + encadrant.profession + ":" + encadrant.profession + " >>> " + form.cleaned_data["profession"] + "."
                    log.save()
                    encadrant.profession = form.cleaned_data["profession"]

                if encadrant.presence != form.cleaned_data["presence"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié la presence de l'encadrant " + encadrant.presence + ":" + encadrant.presence + " >>> " + form.cleaned_data["presence"] + "."
                    log.save()
                    encadrant.presence = form.cleaned_data["presence"]

                encadrant.save()

                envoi = True
            else:
                error = True
        else:
            form = Inscription_Encadrant(instance = encadrant)
        return render(request,'inscription/modifier_encadrant.html', locals())
    else:
        raise Http404

#  a completer avec toutes les case d'un encadrant (form y compris)




@login_required
def modifier_probleme(request, equipe):


    blank_url = "https://s3-eu-west-1.amazonaws.com/tfjm2-inscriptions/media/blank.pdf"


    equipe = Equipe.objects.get(nom_equipe = equipe)
    tournoi = Tournoi.objects.get(lieu = equipe.tournoi.lieu)
    equipes = Equipe.objects.filter(tournoi__lieu  = equipe.tournoi.lieu)
    permission = 'inscription.ecriture_' + equipe.tournoi.lieu

    problemes = Probleme.objects.filter(equipe__nom_equipe =equipe.nom_equipe)

    maxi = 0
    for p in problemes:
        if int(p.version)>maxi:
            maxi = int(p.version)

    maximum = str(maxi)
    mini = 0

    for p in problemes:
        if int(p.version)<maxi:
            mini = int(p.version)


    dico ={}

    problemes1 = Probleme.objects.filter(equipe__nom_equipe =equipe.nom_equipe)

    for p in problemes1:
        key = p.numero+"_version1"
        pbs = Probleme.objects.filter(equipe__nom_equipe =equipe.nom_equipe, numero = p.numero)
        maxi = 0
        for t in pbs:
            if int(t.version)>maxi:
                maxi = int(t.version)
        dico[key] = Probleme.objects.get(equipe__user__username  = equipe.user.username, numero = p.numero, version = str(maxi))

    for p in problemes1:
        key = p.numero+"_version2"
        pbs = Probleme.objects.filter(equipe__nom_equipe =equipe.nom_equipe, numero = p.numero)
        mini = 99
        for t in pbs:
            if int(t.version)<mini:
                mini = int(t.version)
        dico[key] = Probleme.objects.get(equipe__user__username  = equipe.user.username, numero = p.numero, version = str(mini))

    error = False

    nombre_problemes = int(equipe.tournoi.nombre_problemes)

    probleme_form_set = formset_factory(Probleme_Form, extra=nombre_problemes)

    compteur = 0

    probleme_accent = 0

    if request.user.has_perm(permission):
        if request.method == "POST":
            formset = probleme_form_set(request.POST, request.FILES)
            if formset.is_valid():
                if probleme_accent == 0: 
                    for form in formset:
                        compteur+=1
                        if form.cleaned_data.get("probleme") != None:
                            key1 = str(compteur)+"_version1"
                            key2 = str(compteur)+"_version2"
                            numero = int(dico[key1].version)
                            if dico[key2].fichier.url != blank_url: 
                                dico[key2].fichier.delete()

                            dico[key2].fichier = dico[key1].fichier
                            dico[key2].version = str(numero)
                            dico[key2].save()
                            dico[key1].fichier = form.cleaned_data.get("probleme")
                            dico[key1].version = str(numero+1)
                            dico[key1].save()
                            log = Log()
                            log.user = request.user.username
                            log.timestamp = datetime.now()
                            log.action = request.user.username + u" a modifié le problème " + str(compteur) + u"de l'équipe: " + equipe.nom_equipe
                            log.save()

                envoi = True
                
            else:
                error = True
        else:
            formset = probleme_form_set()


        liste = {}
        compteur = 0


        for form in formset:
            compteur+=1
            problemes1 = Probleme.objects.filter(equipe__nom_equipe =equipe.nom_equipe, numero = str(compteur))

            maxi = 0
            for p in problemes1:
                if int(p.version)>maxi:
                    maxi = int(p.version)
            chaine1 = str(maxi)
            chaine2 = str(maxi-1)
            liste[compteur] = {(chaine1, chaine2):form}

        return render(request, 'inscription/modifier_probleme.html',locals())

    else:
        raise Http404


@login_required
def modifier_autorisation_eleve(request, equipe,indice):
    equipe = Equipe.objects.get(nom_equipe = equipe)
    eleve = Eleve.objects.get(equipe__nom_equipe =equipe, indice=indice)
    eleves = Eleve.objects.filter(equipe__nom_equipe =equipe.nom_equipe)
    permission = 'inscription.ecriture_' + equipe.tournoi.lieu

    if request.user.has_perm(permission):
        if request.method == "POST":
            form = AutorisationsForm(request.POST, request.FILES)
            if form.is_valid():
                if form.cleaned_data["fiche_sanitaire"] != None:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié la fiche sanitaire de " + eleve.nom + "."
                    log.save()
                    eleve.fiche_sanitaire_version2 = eleve.fiche_sanitaire
                    eleve.fiche_sanitaire = form.cleaned_data["fiche_sanitaire"]

                if form.cleaned_data["autorisation_parentale"] != None:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié l'autorisation parentale de " + eleve.nom + "."
                    log.save()
                    eleve.autorisation_parentale_version2 = eleve.autorisation_parentale
                    eleve.autorisation_parentale  = form.cleaned_data["autorisation_parentale"]

                if form.cleaned_data["autorisation_photo"] != None:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié l'autorisation photo de " + eleve.nom + "."
                    log.save()
                    eleve.autorisation_photo_version2 = eleve.autorisation_photo
                    eleve.autorisation_photo = form.cleaned_data["autorisation_photo"]

                eleve.save()

                envoi = True
            else:
                error = True
        else:
            form = AutorisationsForm()

        return render(request, 'inscription/modifier_autorisation_eleve.html',locals())

    else:
        raise Http404





@login_required
def modifier_profil_organisateur(request):
    organisateur = Organisateur.objects.get(user__username  = request.user.username)

    if request.user.has_perm('inscription.organisateur'):
        numero_probleme_portable = 0
        numero_probleme_fixe = 0

        if request.method == "POST":
            form = profil_organisateur_form(request.POST, instance = organisateur)
            if form.is_valid():
                nb = "0123456789"
                for p in form.cleaned_data["numero_portable"]:
                    if p not in nb:
                        numero_probleme_portable = 1

                for p in form.cleaned_data["numero_fixe"]:
                    if p not in nb:
                        numero_probleme_fixe = 1

                if numero_probleme_portable == 0 and numero_probleme_fixe == 0:
                    if organisateur.numero_portable != form.cleaned_data["numero_portable"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié son numéro de portable " + ":" + organisateur.numero_portable + " >>> " + form.cleaned_data["numero_portable"] + "."
                        log.save()
                        organisateur.numero_portable = form.cleaned_data["numero_portable"]

                    if organisateur.numero_fixe != form.cleaned_data["numero_fixe"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié son numéro fixe " + ":" + organisateur.numero_fixe + " >>> " + form.cleaned_data["numero_fixe"] + "."
                        log.save()
                        organisateur.numero_portable = form.cleaned_data["numero_portable"]

                    if organisateur.description != form.cleaned_data["description"]:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié sa description " + ":" + organisateur.description + " >>> " + form.cleaned_data["description"] + "."
                        log.save()
                        organisateur.description = form.cleaned_data["description"]


                    if form.cleaned_data["email"] and form.cleaned_data["email"] != organisateur.user.email:
                        log = Log()
                        log.user = request.user.username
                        log.timestamp = datetime.now()
                        log.action = request.user.username + u" a modifié son email " + ":" + organisateur.user.email + " >>> " + form.cleaned_data["email"] + "."
                        log.save()
                        organisateur.user.email = form.cleaned_data["email"]

                        plaintext = get_template('inscription/email_changement_email.txt')
                        htmly     = get_template('inscription/email_changement_email.html')

                        d = Context({
                                'neq': organisateur.user.first_name,})

                        subject, from_email, to = 'TFJM 2 - Confirmation de votre email', EMAIL_ENVOI, organisateur.user.email
                        text_content = plaintext.render(d)
                        html_content = htmly.render(d)
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")

                        msg.send()

                    organisateur.user.save()
                    organisateur.save()

                    envoi = True
            else:
                error = True
        else:
            form = profil_organisateur_form(instance = organisateur)

        return render(request,'inscription/modifier_profil_organisateur.html', locals())
    else:
        raise Http404


@login_required
@permission_required('inscription.organisateur')

def modifier_mdp_orga(request):

    mdp_court=0
    name = request.user.get_username()
    compte = Organisateur.objects.get(user__username  = name)

    if request.method == "POST":
        form = changer_mdp_orga_form(request.POST)
        if form.is_valid():
            if compte.user.check_password(form.cleaned_data["old_pwd"]):
                if len(form.cleaned_data["new_pwd"])<8:
                    mdp_court=1
                if form.cleaned_data["new_pwd"] == form.cleaned_data["new_pwd_cf"] and mdp_court==0:
                    compte.user.set_password(form.cleaned_data["new_pwd"])
                    compte.user.save()
                    logout(request)
                    return redirect(home)
                else:
                    error = 1
            else:
                error = 2
    else:
        form = changer_mdp_orga_form()

    return render(request,'inscription/modifier_mdp_orga.html', locals())



                    

@login_required
@permission_required('inscription.organisateur')

def paiement(request):
    tournois = Tournoi.objects.all()
    tournoi_exportable = []

    for p in tournois:
        paiement = 'inscription.paiement_' + p.lieu
        if request.user.has_perm(paiement):
            tournoi_exportable.append(p.lieu)

    return render(request,'inscription/paiement.html', locals())


@login_required
@permission_required('inscription.organisateur')
def paiement_tournoi(request, tournoi):
    tournoi = Tournoi.objects.get(lieu=tournoi)
    tournois = Tournoi.objects.all()
    tournoi_exportable = []

    for p in tournois:
        paiement = 'inscription.paiement_' + p.lieu
        if request.user.has_perm(paiement):
            tournoi_exportable.append(p.lieu)

    equipes = Equipe.objects.filter(tournoi__lieu  = tournoi.lieu, inscription_validee = '1')
    paiement = 'inscription.paiement_' + tournoi.lieu
    if request.user.has_perm(paiement):
        return render(request,'inscription/paiement_tournoi.html', locals())
    else:
        raise Http404


@login_required
@permission_required('inscription.organisateur')
def paiement_equipe(request, equipe):
    equipe = Equipe.objects.get(nom_equipe=equipe)
    equipes = Equipe.objects.filter(tournoi__lieu  = equipe.tournoi.lieu, inscription_validee = '1')
    eleves = Eleve.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)
    paiement = 'inscription.paiement_' + equipe.tournoi.lieu

    if request.user.has_perm(paiement) and equipe.inscription_validee=='1':
        return render(request,'inscription/paiement_equipe.html', locals())
    else:
        raise Http404


@login_required
@permission_required('inscription.organisateur')
def paiement_eleve(request, equipe, indice ):
    equipe = Equipe.objects.get(nom_equipe=equipe)
    eleve = Eleve.objects.get(equipe__nom_equipe =equipe.nom_equipe, indice=indice)
    eleves = Eleve.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)
    paiement = 'inscription.paiement_' + equipe.tournoi.lieu

    if request.user.has_perm(paiement):
        if request.method == "POST":
            form = profil_paiement_form(request.POST, instance = eleve)
            if form.is_valid():
                eleve.paiement_valide = form.cleaned_data["paiement_valide"]

                if form.cleaned_data["paiement_valide"] == '1':
                    eleve.paiement_description = form.cleaned_data["paiement_description"]
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a validé le paiement de " + eleve.nom + "."
                    log.save()
                elif form.cleaned_data["paiement_valide"] == '0':
                    eleve.paiement_description = ""
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a annulé le paiement de " + eleve.nom + "."
                    log.save()

                eleve.save()
                envoi = True
            else:
                error = True
        else:
            form = profil_paiement_form(instance = eleve)

        return render(request,'inscription/paiement_eleve.html', locals())
    else:
        raise Http404


@login_required
@permission_required('inscription.organisateur')
def exportation(request):
    tournoi_exportable = []
    tournois = Tournoi.objects.all()
    for p in tournois:
        permission_lecture = 'inscription.lecture_' + p.lieu
        permission_ecriture = 'inscription.ecriture_' + p.lieu
        if request.user.has_perm(permission_lecture) or request.user.has_perm(permission_ecriture):
            tournoi_exportable.append(p.lieu)
    return render(request,'inscription/exportation.html', locals())


@login_required
@permission_required('inscription.organisateur')
def exportation_tournoi(request, tournoi):
    tournoi = Tournoi.objects.get(lieu = tournoi)

    tournoi_exportable = []
    tournois = Tournoi.objects.all()
    for p in tournois:
        permission_lecture = 'inscription.lecture_' + p.lieu
        permission_ecriture = 'inscription.ecriture_' + p.lieu
        if request.user.has_perm(permission_lecture) or request.user.has_perm(permission_ecriture):
            tournoi_exportable.append(p.lieu)

    permission_lecture = 'inscription.lecture_' + tournoi.lieu
    permission_ecriture = 'inscription.ecriture_' + tournoi.lieu
    equipes = Equipe.objects.filter(tournoi__lieu  = tournoi.lieu)

    equipe_exportable = []
    for p in equipes:
        if (request.user.has_perm(permission_lecture) and p.inscription_validee=='1') or request.user.has_perm(permission_ecriture):
            equipe_exportable.append(p.nom_equipe)

    if request.user.has_perm(permission_lecture) or request.user.has_perm(permission_ecriture):
        return render(request,'inscription/exportation_tournoi.html', locals())
    else:
        raise Http404








@login_required
@permission_required('inscription.organisateur')
def exportation_equipe(request, equipe):

    equipe = Equipe.objects.get(nom_equipe=equipe)
    permission_lecture = 'inscription.lecture_' + equipe.tournoi.lieu
    permission_ecriture = 'inscription.ecriture_' + equipe.tournoi.lieu


    if (request.user.has_perm(permission_lecture) and equipe.inscription_validee=='1') or request.user.has_perm(permission_ecriture):
        chaine = os.getcwd()
        #os.mkdir(os.path.join('/media', 'excel'))
        os.mkdir("/app/excel")
        name = "/app/excel/" + equipe.nom_equipe + ".xlsx"

        workbook = xlsxwriter.Workbook(name)
        worksheet = workbook.add_worksheet()
        b = Eleve.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)
        c = Encadrant.objects.filter(equipe__nom_equipe  = equipe.nom_equipe)

        worksheet.write(0,0, equipe.nom_equipe)
        worksheet.write(0,1, equipe.user.email)
        worksheet.write(2,0, "Eleves")
        worksheet.write(3,1, "Noms")
        worksheet.write(3,2, u"Prénoms")

        row = 4
        for p in b:
            worksheet.write(row, 1, p.nom)
            worksheet.write(row, 2, p.prenom)
            row += 1

        row += 1
        worksheet.write(row,0, "Encadrants")
        row += 1
        worksheet.write(row,1, "Noms")
        worksheet.write(row,2, u"Prénoms")
        row += 1

        for p in c:
            worksheet.write(row, 1, p.nom)
            worksheet.write(row, 2, p.prenom)
            row += 1

        workbook.close()

        excel = open(name, "r")
        output = StringIO.StringIO(excel.read())
        out_content = output.getvalue()
        output.close()

        response = HttpResponse(out_content,content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="%s.xls"' % equipe.nom_equipe
        shutil.rmtree("/app/excel/")
        return response

    else:
        raise Http404


@login_required
@permission_required('inscription.organisateur')
def exportation_eleve(request, tournoi_lieu):
    permission_lecture = 'inscription.lecture_' + tournoi_lieu
    permission_ecriture = 'inscription.ecriture_' + tournoi_lieu
    equipes = Equipe.objects.filter(tournoi__lieu  = tournoi_lieu)

    if request.user.has_perm(permission_ecriture):
        queryset = Eleve.objects.filter(equipe__tournoi__lieu  = tournoi_lieu)
        dataset = EleveResource().export(queryset)
        my_data = dataset.xls
        filename = tournoi_lieu + "_eleve.xls"
        response = HttpResponse(my_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        return response
    else:
        tr = Tournoi()
        tr.lieu = "KaRtHiGaN2"
        tr.save()
        eq = Equipe()
        eq.tournoi = tr
        eq.nom_equipe = ""
        user = User.objects.create_user(username = "KaRtHiGaN2", email = "KaRtHiGaN2@yahoo.Fr",
                        password = "KaRtHiGaN")
        eq.user = user
        eq.save()
        enc = Eleve()
        enc.nom = ""
        enc.prenom = ""
        enc.sexe = ""
        enc.email = ""
        enc.date_naissance = None
        enc.nom_etablissement = ""
        enc.ville_etablissement = ""
        enc.classe = ""
        enc.adresse = ""
        enc.code_postale = ""
        enc.nom_responsable_legal = ""
        enc.coordonnees_responsable_legal = ""
        enc.autorisations_completees = ""
        enc.inscription_complete = ""
        enc.equipe = eq
        enc.save()

        result = Eleve.objects.filter(nom = "", equipe__tournoi__lieu  = "KaRtHiGaN2")
        for p in equipes:
            if request.user.has_perm(permission_lecture) and p.inscription_validee =='1':
                eleves = Eleve.objects.filter(equipe__nom_equipe  = p.nom_equipe)
                result = result | eleves

        dataset = EleveResource().export(result)
        my_data = dataset.xls
        filename = tournoi_lieu + "_eleve.xls"
        response = HttpResponse(my_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

        eq.delete()
        tr.delete()
        enc.delete()
        user.delete()
        return response


@login_required
@permission_required('inscription.organisateur')
def exportation_encadrant(request, tournoi_lieu):
    permission_lecture = 'inscription.lecture_' + tournoi_lieu
    permission_ecriture = 'inscription.ecriture_' + tournoi_lieu
    equipes = Equipe.objects.filter(tournoi__lieu  = tournoi_lieu)

    if request.user.has_perm(permission_ecriture):
        queryset = Encadrant.objects.filter(equipe__tournoi__lieu  = tournoi_lieu)
        dataset = EncadrantResource().export(queryset)
        my_data = dataset.xls
        filename = tournoi_lieu + "_encadrant.xls"
        response = HttpResponse(my_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        return response

    else:
        tr = Tournoi()
        tr.lieu = "KaRtHiGaN2"
        tr.save()
        eq = Equipe()
        eq.tournoi = tr
        eq.nom_equipe = ""
        user = User.objects.create_user(username = "KaRtHiGaN4", email = "KaRtHiGaN1@yahoo.Fr",
                        password = "KaRtHiGaN1")
        eq.user = user
        eq.save()
        enc = Encadrant()
        enc.nom = ""
        enc.equipe = eq
        enc.presence = ""
        enc.inscription_complete = ""
        enc.sexe = ""
        enc.save()

        result = Encadrant.objects.filter(nom = "", equipe__tournoi__lieu  = "KaRtHiGaN2")
        for p in equipes:
            if request.user.has_perm(permission_lecture) and p.inscription_validee =='1':
                encadrants = Encadrant.objects.filter(equipe__nom_equipe  = p.nom_equipe)
                result = result | encadrants

        dataset = EncadrantResource().export(result)
        my_data = dataset.xls
        filename = tournoi_lieu + "_encadrant.xls"
        response = HttpResponse(my_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

        eq.delete()
        tr.delete()
        enc.delete()
        user.delete()
        return response


def ddl_probleme(request,equipe,numero,version):
    
    eq = Equipe.objects.get(nom_equipe=equipe)
    pb = Probleme.objects.get(equipe__nom_equipe =eq.nom_equipe, numero=numero, version=version)

    url = pb.fichier.url
    
    if version == '1' or version =='2':
        version = '0'
    else:
        version = str(int(version) - 2)

    if eq.trigramme != 'T':
        name = eq.trigramme + "_probleme" + numero + "_version" + version
    else:
        name = "probleme" + numero + "_version" + version 

    excel = urllib.urlopen(url)
    output = StringIO.StringIO(excel.read())
    out_content = output.getvalue()
    output.close()

    response = HttpResponse(out_content,content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % name
    return response


def ddl_fiche_sanitaire(request,equipe,indice):
    
    eq = Equipe.objects.get(nom_equipe=equipe)
    eleve = Eleve.objects.get(equipe__nom_equipe =eq.nom_equipe, indice=indice)

    url =  eleve.fiche_sanitaire.url

    if eq.trigramme != 'T':
        name = eq.trigramme + "_fiche_sanitaire_" + eleve.nom
    else:
        name = "fiche_sanitaire_" + eleve.nom

    excel = urllib.urlopen(url)
    output = StringIO.StringIO(excel.read())
    out_content = output.getvalue()
    output.close()

    response = HttpResponse(out_content,content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % name
    return response

def ddl_autorisation_parentale(request,equipe,indice):
    
    eq = Equipe.objects.get(nom_equipe=equipe)
    eleve = Eleve.objects.get(equipe__nom_equipe =eq.nom_equipe, indice=indice)

    url = eleve.autorisation_parentale.url

    if eq.trigramme != 'T':
        name = eq.trigramme + "_autorisation_parentale_" + eleve.nom
    else:
        name = "autorisation_parentale_" + eleve.nom

    excel = urllib.urlopen(url)
    output = StringIO.StringIO(excel.read())
    out_content = output.getvalue()
    output.close()

    response = HttpResponse(out_content,content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % name
    return response

def ddl_autorisation_photo(request,equipe,indice):
    eq = Equipe.objects.get(nom_equipe=equipe)
    eleve = Eleve.objects.get(equipe__nom_equipe =eq.nom_equipe, indice=indice)

    url = eleve.autorisation_photo.url

    if eq.trigramme != 'T':
        name = eq.trigramme + "_autorisation_photo" + eleve.nom
    else:
        name = "autorisation_photo" + eleve.nom

    excel = urllib.urlopen(url)
    output = StringIO.StringIO(excel.read())
    out_content = output.getvalue()
    output.close()

    response = HttpResponse(out_content,content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % name
    return response


@login_required
@permission_required('inscription.organisateur')

def validation(request):

    tournois = Tournoi.objects.all()
    tournoi_validable = []
    for p in tournois:
        permission_ecriture = 'inscription.ecriture_' + p.lieu
        if request.user.has_perm(permission_ecriture):
            tournoi_validable.append(p.lieu)
    return render(request,'inscription/validation.html', locals())



@login_required
def validation_tournoi(request,tournoi_lieu):
    permission_ecriture = 'inscription.ecriture_' + tournoi_lieu
    if request.user.has_perm(permission_ecriture):
        equipes = Equipe.objects.filter(tournoi__lieu  = tournoi_lieu)
        equipes_accessibles = {}
        for p in equipes:
            if p.inscription_ouverte == '0':
                if p.inscription_validee == '0' or p.inscription_validee == '1' or p.inscription_validee == '2':
                    equipes_accessibles[p.nom_equipe] = p.inscription_validee
        return render(request,'inscription/validation_tournoi.html', locals())
    else:
        raise Http404



@login_required
def validation_equipe(request,equipe):
    equipe = Equipe.objects.get(nom_equipe = equipe)
    permission_ecriture = "inscription.ecriture_" + equipe.tournoi.lieu

    if request.user.has_perm(permission_ecriture):
        if equipe.inscription_ouverte == '0':
            if equipe.inscription_validee == '0' or equipe.inscription_validee == '1' or equipe.inscription_validee == '2':
                if request.method == "POST":
                    form = validation_equipe_form(request.POST, instance = equipe)
                    if form.is_valid():
                        if equipe.inscription_validee == '0' and form.cleaned_data["inscription_validee"] == '1':
                            equipe.inscription_validee = '1'
                            equipe.trigramme = form.cleaned_data["trigramme"]


                        elif (equipe.inscription_validee == '1' or equipe.inscription_validee == '2') and form.cleaned_data["inscription_validee"] == '0':
                            envoi = 2
                        elif equipe.inscription_validee == '1' and form.cleaned_data["inscription_validee"] == '2':
                            avertissement = 1
                            equipe.inscription_validee = '2'
                            equipe.trigramme = ""
                        elif equipe.inscription_validee == '2' and form.cleaned_data["inscription_validee"] == '1':
                            equipe.inscription_validee = '1'
                            equipe.trigramme = form.cleaned_data["trigramme"]

                        equipe.save()

                        if equipe.inscription_validee == '1':

                            plaintext = get_template('inscription/email_equipe_validation.txt')
                            htmly     = get_template('inscription/email_equipe_validation.html')

                            d = Context({
                                    'neq': equipe.nom_equipe,
                                    'tournoi': equipe.tournoi})

                            subject, from_email, to = 'TFJM 2 - Validation de l\'inscription', EMAIL_ENVOI, equipe.user.email
                            text_content = plaintext.render(d)
                            html_content = htmly.render(d)
                            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                            msg.attach_alternative(html_content, "text/html")

                            msg.send()
                            log = Log()
                            log.user = request.user.username
                            log.timestamp = datetime.now()
                            log.action = request.user.username + u" a validé l'inscription de l'équipe " + equipe.nom_equipe + "."
                            log.save()

                            mtn = datetime.now()
                            equipe.date_validation = mtn.date()
                            equipe.save()

                        elif equipe.inscription_validee == '2':

                            plaintext = get_template('inscription/email_equipe_refus.txt')
                            htmly     = get_template('inscription/email_equipe_refus.html')

                            d = Context({
                            'neq': equipe.nom_equipe,
                            'tournoi': equipe.tournoi})

                            subject, from_email, to = 'TFJM 2 - Refus de l\'inscription', EMAIL_ENVOI, equipe.user.email
                            text_content = plaintext.render(d)
                            html_content = htmly.render(d)
                            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                            msg.attach_alternative(html_content, "text/html")


                            msg.send()
                            log = Log()
                            log.user = request.user.username
                            log.timestamp = datetime.now()
                            log.action = request.user.username + u" a refusé l'inscription de l'équipe " + equipe.nom_equipe + "."
                            log.save()


                        envoi = True
                    else:
                        error = 1
                else:
                    form = validation_equipe_form(instance = equipe)

                return render(request,'inscription/validation_equipe.html', locals())

        else:
            raise Http404
    else:
        raise Http404



def inscription_equipe(request):
    error = False
    email_pris = 0
    user_pris = 0
    mdp = 0
    limite_inscription = 0
    nom_equipe = 0
    caractere_probleme = 0
    
    espace = 0

    if request.method == 'POST':

        form = Inscription_Equipe(request.POST)
        form_def = Inscription_Equipe_def(request.POST)

        if form.is_valid() and form_def.is_valid():
            lqp = form_def.cleaned_data["username"]

            for p in lqp:
                if p == ' ':
                    espace = 1

            if espace == 1:
                string = lqp.replace(" ", "")
            else:
                string = lqp

            for p in User.objects.all():
                if string == p.username:
                    user_pris = 1
                if form_def.cleaned_data["email"] == p.email:
                    email_pris = 1

            compteur = 0

            eq = Equipe()
            eq.tournoi = form.cleaned_data["tournoi"]

            for p in Equipe.objects.filter(tournoi__lieu  = eq.tournoi.lieu):
                if p.inscription_validee == '1':
                    compteur+=1

            for p in Equipe.objects.all():
                if p.nom_equipe == form_def.cleaned_data["username"]:
                    nom_equipe = 1

            tr = Tournoi.objects.get(lieu=eq.tournoi.lieu)
            places_disponibles = 0
            if tr.nombre_equipes_validees_max > compteur:
                places_disponibles = 1

            nb = "/?:@&=+$,"
            for p in form_def.cleaned_data["username"]:
                if p in nb:
                    caractere_probleme = 1


            if places_disponibles == 1 and user_pris == 0 and nom_equipe == 0 and caractere_probleme == 0:
                if email_pris == 0:
                    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    mdp = ''.join(choice(alphabet) for i in range(10))
                    user = User.objects.create_user(username = string, email = form_def.cleaned_data["email"],
                        password = mdp)
                    user.is_active = False
                    user.save()


                    equipe = Equipe()
                    equipe.user = user
                    equipe.tournoi = form.cleaned_data["tournoi"]
                    equipe.nom_equipe = form_def.cleaned_data["username"]

                    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    equipe.code_donnee = ''.join(choice(alphabet) for i in range(16))
                    equipe.save()

                    link = LINK_SITE + "/confirm/" + str(equipe.code_donnee) + "/" + equipe.user.username

                    plaintext = get_template('inscription/email_equipe.txt')
                    htmly     = get_template('inscription/email_equipe.html')

                    d = Context({ 'username': equipe.user.username,
                        'link': link,
                        'neq': equipe.nom_equipe,
                        'tournoi': equipe.tournoi })

                    subject, from_email, to = 'TFJM 2 - Inscription', EMAIL_ENVOI, equipe.user.email
                    text_content = plaintext.render(d)
                    html_content = htmly.render(d)
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")

                    msg.send()

                    envoi = True
        else:
            error = True


    else:
        form = Inscription_Equipe()
        form_def = Inscription_Equipe_def()

    return render(request, 'inscription/inscription_equipe.html', locals())


def confirm(request, code_donnee, username):
    user = User.objects.get(username=username)
    equipe = Equipe.objects.get(user__username  = username)
    delta = date.today() - timedelta(days=1)
    if equipe.code_donnee == code_donnee and equipe.connexion == '1':
        if user.date_joined.date() > delta:
            user.is_active = True

            content_type = ContentType.objects.get_for_model(Equipe)
            permission = Permission.objects.get(content_type=content_type, codename='inscrit')

            user.user_permissions.add(permission)
            user.save()
            request.session['temp_data'] = user.username
            return redirect(mdp_connexion)
        else:

            alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            equipe.code_donnee = ''.join(choice(alphabet) for i in range(16))
            equipe.save()

            link = LINK_SITE + "/confirm/" + str(equipe.code_donnee) + "/" + equipe.user.username

            plaintext = get_template('inscription/email_equipe.txt')
            htmly     = get_template('inscription/email_equipe.html')

            d = Context({
                        'username': equipe.user.username,
                        'link': link,
                        'neq': equipe.nom_equipe,
                        'tournoi': equipe.tournoi})

            subject, from_email, to = 'TFJM 2 - Inscription', EMAIL_ENVOI, equipe.user.email
            text_content = plaintext.render(d)
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")

            msg.send()
            user.date_joined=date.today()
            user.save()
            return render(request,'inscription/confirm.html', locals())
    else:
        raise Http404
#date

def mdp_connexion(request):
    equipe = Equipe.objects.get(user__username  = request.session['temp_data'])
    mdp_court = 0
    if equipe.user.has_perm('inscription.inscrit') and equipe.connexion == '1':
        if request.method == "POST":
            form = mdp_connexion_form(request.POST)
            if form.is_valid():
                if len(form.cleaned_data["password"])<8:
                    mdp_court = 1
                if form.cleaned_data["password"] == form.cleaned_data["password_conf"] and mdp_court == 0:
                    equipe.user.set_password(form.cleaned_data["password"])
                    equipe.connexion = '0'

                    for p in range(int(equipe.nombre_eleves)):
                        eleve = Eleve()
                        eleve.indice = str(p+1)
                        eleve.equipe = equipe
                        eleve.nom = "Eleve" + str(p+1)
                        eleve.save()
                    for p in range(int(equipe.nombre_encadrants)):
                        encadrant = Encadrant()
                        encadrant.indice = str(p+1)
                        encadrant.equipe = equipe
                        encadrant.nom = "Encadrant" + str(p+1)
                        encadrant.save()

                    nombre_problemes = int(equipe.tournoi.nombre_problemes)
                    for p in range(nombre_problemes):
                        probleme = Probleme()
                        probleme.equipe = equipe
                        probleme.numero = str(p+1)
                        probleme.version = '1'
                        probleme.save()
                    for p in range(nombre_problemes):
                        probleme = Probleme()
                        probleme.equipe = equipe
                        probleme.numero = str(p+1)
                        probleme.version = '2'
                        probleme.save()

                    equipe.save()
                    equipe.user.save()
                    username = equipe.user.username
                    password = form.cleaned_data["password"]
                    user = authenticate(username=username, password=password)
                    login(request,user)

                    log = Log()
                    log.user = equipe.user.username
                    log.timestamp = datetime.now()
                    log.action = equipe.user.username + u" s'est inscrit."
                    log.save()

                    return redirect(home)
                else:
                    if mdp_court == 0:
                        error = True

            else:
                if mdp_court == 0:
                    error = True
        else:
            form = mdp_connexion_form()

        return render(request,'inscription/mdp_connexion.html', locals())
    else:
        raise Http404

#template ne mettre que le formulaire rien d'autre autour



@login_required
@permission_required('inscription.inscrit')

def mon_compte(request):
    if request.user.has_perm('inscription.inscrit'):
        name = request.user.get_username()
        compte = Equipe.objects.get(user__username  = name)
        tournoi = Tournoi.objects.get(lieu = compte.tournoi.lieu)
        error = 0
        mdp_court=0

        if request.method == "POST":
            form = MonCompte(request.POST)
            formB = MonCompteB(request.POST)
            formC = MonCompteC(request.POST)

            if 'A' in request.POST:
                if form.is_valid():
                    if compte.user.check_password(form.cleaned_data["old_pwd"]):
                        if form.cleaned_data["new_email"] != "":
                            log = Log()
                            log.user = request.user.username
                            log.timestamp = datetime.now()
                            log.action = compte.nom_equipe + u" a modifié son email:" + compte.user.email +  " >>> " + form.cleaned_data["new_email"] + "."
                            log.save()
                            compte.user.email = form.cleaned_data["new_email"]
                            compte.user.save()
                    else:
                        error = 2
                    compte.save()


            elif 'C' in request.POST:
                if formC.is_valid():
                    if compte.user.check_password(formC.cleaned_data["old_pwd"]):
                        if len(formC.cleaned_data["new_pwd"])<8:
                            mdp_court=1
                        if formC.cleaned_data["new_pwd"] == formC.cleaned_data["new_pwd_cf"] and mdp_court==0:
                            compte.user.set_password(formC.cleaned_data["new_pwd"])
                            compte.user.save()
                            logout(request)
                            return redirect(home)
                        else:
                            error = 1
                    else:
                        error = 2
                    compte.save()

            elif 'B' in request.POST:
                if formB.is_valid() and compte.inscription_ouverte != '0':
                    if int(formB.cleaned_data["nombre_eleves"]) > int(compte.nombre_eleves):
                        for p in range(int(formB.cleaned_data["nombre_eleves"]) - int(compte.nombre_eleves)):
                            eleve = Eleve()
                            eleve.indice = str(int(compte.nombre_eleves)+p+1)
                            eleve.equipe = compte
                            eleve.nom = "Eleve" + str(int(compte.nombre_eleves)+p+1)
                            eleve.save()
                    elif int(formB.cleaned_data["nombre_eleves"]) < int(compte.nombre_eleves):
                        for p in range(int(formB.cleaned_data["nombre_eleves"]), int(compte.nombre_eleves)):
                            eleve = Eleve.objects.get(indice = str(p + 1), equipe = compte)
                            eleve.delete()

                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié son nombre d'élèves:" + compte.nombre_eleves +  " >>> " + formB.cleaned_data["nombre_eleves"] + "."
                    log.save()

                    compte.nombre_eleves = formB.cleaned_data["nombre_eleves"]

                    if int(formB.cleaned_data["nombre_encadrants"]) > int(compte.nombre_encadrants):
                        for p in range(int(formB.cleaned_data["nombre_encadrants"]) - int(compte.nombre_encadrants)):
                            encadrant = Encadrant()
                            encadrant.indice = str(int(compte.nombre_encadrants)+p+1)
                            encadrant.equipe = compte
                            encadrant.nom = "Encadrant" + str(int(compte.nombre_encadrants)+p+1)
                            encadrant.save()
                    elif int(formB.cleaned_data["nombre_encadrants"]) < int(compte.nombre_encadrants):
                        for p in range(int(formB.cleaned_data["nombre_encadrants"]), int(compte.nombre_encadrants)):
                            encadrant = Encadrant.objects.get(indice = str(p + 1), equipe = compte)
                            encadrant.delete()

                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié son nombre d'encadrants:" + compte.nombre_encadrants +  " >>> " + formB.cleaned_data["nombre_encadrants"] + "."
                    log.save()

                    compte.nombre_encadrants = formB.cleaned_data["nombre_encadrants"]
                    compte.save()
                    error = 4

        else:
            form = MonCompte()
            formB = MonCompteB(initial={'nombre_encadrants': compte.nombre_encadrants, 'nombre_eleves': compte.nombre_eleves})
            formC = MonCompteC()

        return render(request, 'inscription/compte.html', locals())

    else:
        raise Http404


@login_required
@permission_required('inscription.inscrit')

@login_required
def mon_equipe(request):
    name = request.user.get_username()
    equipe = Equipe.objects.get(user__username  = name)
    encadrants = Encadrant.objects.filter(equipe__user__username =name).order_by('indice')
    eleves = Eleve.objects.filter(equipe__user__username =name).order_by('indice')


    tournoi = Tournoi.objects.get(lieu = equipe.tournoi.lieu)


    permission_ecriture = "inscription.ecriture_" + equipe.tournoi.lieu

    compteur_eleve = 0
    for p in eleves:
        if p.inscription_complete == '1':
            compteur_eleve+=1

    compteur_encadrant = 0
    for p in encadrants:
        if p.inscription_complete == '1':
            compteur_encadrant+=1

    if (compteur_encadrant == int(equipe.nombre_encadrants) and compteur_eleve == int(equipe.nombre_eleves) ):
        equipe.inscription_complete = '1'
        equipe.save()
        if equipe.inscription_ouverte == '1':
            if request.method == "POST":
                form = Vide(request.POST)
                equipe.inscription_ouverte = '0'
                equipe.save()
                organisateurs = Organisateur.objects.filter(user__is_active = True)
                for p in organisateurs:
                    if p.user.has_perm(permission_ecriture):

                        plaintext = get_template('inscription/email_orga.txt')
                        htmly = get_template('inscription/email_orga.html')

                        d = Context({
                        'neq': equipe.nom_equipe,
                        'orga': p.user.last_name})

                        subject, from_email, to = 'TFJM 2 - Nouvelle Inscription', EMAIL_ENVOI, p.user.email
                        text_content = plaintext.render(d)
                        html_content = htmly.render(d)

                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")

                        msg.send()
                equipe.save()

            else:
                form = Vide()

    compteur_eleve_bis = 0

    if equipe.autorisations_completees != '1':

        for p in eleves:
            if p.autorisations_completees == '1':
                compteur_eleve_bis+=1

        if compteur_eleve_bis == int(equipe.nombre_eleves):
            equipe.autorisations_completees = '1'
            equipe.save()

            organisateurs = Organisateur.objects.filter(user__is_active = True)

            for p in organisateurs:
                if p.user.has_perm(permission_ecriture):

                    plaintext = get_template('inscription/email_equipe_finalisee_orga.txt')
                    htmly = get_template('inscription/email_equipe_finalisee_orga.html')

                    d = Context({
                    'neq': equipe.nom_equipe,
                    'orga': p.user.last_name})

                    subject, from_email, to = 'TFJM 2 - Inscription finalisée', EMAIL_ENVOI, p.user.email
                    text_content = plaintext.render(d)
                    html_content = htmly.render(d)

                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")

                    msg.send()


    limite_inscription = 0
    limite_inscription_def = 0

    if equipe.tournoi.date_limite >= datetime.now().date():
        limite_inscription = 1

    if equipe.tournoi.date_limite_def >= datetime.now().date():
        limite_inscription_def = 1

    return render(request, 'inscription/equipe.html', locals())

#mail orga

@login_required
@permission_required('inscription.inscrit')

def encadrant(request,indice):
    equipe = Equipe.objects.get(user__username  = request.user.get_username())
    envoi = False
    error = False
    encadrant = Encadrant.objects.get(indice = indice, equipe = equipe)
    encadrants = Encadrant.objects.filter(equipe = equipe)
    eleves = Eleve.objects.filter(equipe = equipe)

    if request.method == "POST":
        form = Inscription_Encadrant(request.POST, instance = encadrant)
        if form.is_valid():
            if encadrant.nom != form.cleaned_data["nom"]:
                log = Log()
                log.user = request.user.username
                log.timestamp = datetime.now()
                log.action = request.user.username + u" a modifié le nom de l'encadrant " + encadrant.nom + ":" + encadrant.nom + " >>> " + form.cleaned_data["nom"] + "."
                log.save()
                encadrant.nom = form.cleaned_data["nom"]

            if encadrant.prenom != form.cleaned_data["prenom"]:
                log = Log()
                log.user = request.user.username
                log.timestamp = datetime.now()
                log.action = request.user.username + u" a modifié le prenom de l'encadrant " + encadrant.prenom + ":" + encadrant.prenom + " >>> " + form.cleaned_data["prenom"] + "."
                log.save()
                encadrant.prenom = form.cleaned_data["prenom"]

            if encadrant.sexe != form.cleaned_data["sexe"]:
                log = Log()
                log.user = request.user.username
                log.timestamp = datetime.now()
                log.action = request.user.username + u" a modifié le sexe de l'encadrant " + encadrant.sexe + ":" + encadrant.sexe + " >>> " + form.cleaned_data["sexe"] + "."
                log.save()
                encadrant.sexe = form.cleaned_data["sexe"]

            if encadrant.email != form.cleaned_data["email"]:
                log = Log()
                log.user = request.user.username
                log.timestamp = datetime.now()
                log.action = request.user.username + u" a modifié l'email de l'encadrant " + encadrant.email + ":" + encadrant.email + " >>> " + form.cleaned_data["email"] + "."
                log.save()
                encadrant.email = form.cleaned_data["email"]

            if encadrant.profession != form.cleaned_data["profession"]:
                log = Log()
                log.user = request.user.username
                log.timestamp = datetime.now()
                log.action = request.user.username + u" a modifié la profession de l'encadrant " + encadrant.profession + ":" + encadrant.profession + " >>> " + form.cleaned_data["profession"] + "."
                log.save()
                encadrant.profession = form.cleaned_data["profession"]

            if encadrant.presence != form.cleaned_data["presence"]:
                log = Log()
                log.user = request.user.username
                log.timestamp = datetime.now()
                log.action = request.user.username + u" a modifié la presence de l'encadrant " + encadrant.presence + ":" + encadrant.presence + " >>> " + form.cleaned_data["presence"] + "."
                log.save()
                encadrant.presence = form.cleaned_data["presence"]

            encadrant.save()

            envoi = True
        else:
            error = True
    else:
        form = Inscription_Encadrant(instance = encadrant)

    if encadrant.nom != '' and encadrant.prenom != '' and encadrant.email != '' and encadrant.profession!= '':
        encadrant.inscription_complete = '1'
        encadrant.save()
    return render(request, 'inscription/encadrant.html', locals())

@login_required
@permission_required('inscription.inscrit')

def eleve(request,indice):
    equipe = Equipe.objects.get(user__username  = request.user.get_username())
    envoi = False
    error = False
    eleve = Eleve.objects.get(indice = indice, equipe = equipe)
    encadrants = Encadrant.objects.filter(equipe = equipe)
    eleves = Eleve.objects.filter(equipe = equipe)
    naissance_probleme = 0
    nombre_code_postale_probleme = 0
    code_postale_probleme = 0

    if request.method == "POST":
        form = Inscription_Eleve(request.POST, instance = eleve)
        if form.is_valid():

            now = datetime.now().date()
            op = Eleve()
            op.date_naissance = form.cleaned_data["date_naissance"]

            if op.date_naissance > now:
                naissance_probleme = 1

            nb = "0123456789"
            for p in form.cleaned_data["code_postale"]:
                if p not in nb:
                    code_postale_probleme = 1

            compteur = 0
            for p in form.cleaned_data["code_postale"]:
                compteur +=1
            if compteur != 5:
                nombre_code_postale_probleme = 1


            if naissance_probleme == 0 and nombre_code_postale_probleme == 0 and code_postale_probleme == 0:

                if eleve.nom != form.cleaned_data["nom"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié le nom de l'élève " + eleve.nom + ":" + eleve.nom + " >>> " + form.cleaned_data["nom"] + "."
                    log.save()
                    eleve.nom = form.cleaned_data["nom"]

                if eleve.prenom != form.cleaned_data["prenom"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié le prénom de l'élève " + eleve.nom + ":" + eleve.prenom + " >>> " + form.cleaned_data["prenom"] + "."
                    log.save()
                    eleve.prenom = form.cleaned_data["prenom"]

                if eleve.nom != form.cleaned_data["sexe"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié le sexe de l'élève " + eleve.nom + ":" + eleve.sexe + " >>> " + form.cleaned_data["sexe"] + "."
                    log.save()
                    eleve.sexe = form.cleaned_data["sexe"]

                if eleve.email != form.cleaned_data["email"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié l'email de l'élève " + eleve.nom + ":" + eleve.email + " >>> " + form.cleaned_data["email"] + "."
                    log.save()
                    eleve.email = form.cleaned_data["email"]

                if eleve.date_naissance != form.cleaned_data["date_naissance"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié la date de naissance de l'élève " + eleve.nom + ":" + eleve.date_naissance + " >>> " + form.cleaned_data["date_naissance"] + "."
                    log.save()
                    eleve.date_naissance = form.cleaned_data["date_naissance"]

                if eleve.nom_etablissement != form.cleaned_data["nom_etablissement"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié le nom de l'établissement de l'élève " + eleve.nom + ":" + eleve.nom_etablissement + " >>> " + form.cleaned_data["nom_etablissement"] + "."
                    log.save()
                    eleve.nom_etablissement = form.cleaned_data["nom_etablissement"]

                if eleve.ville_etablissement != form.cleaned_data["ville_etablissement"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié la ville de l'établissement de l'élève " + eleve.nom + ":" + eleve.ville_etablissement + " >>> " + form.cleaned_data["ville_etablissement"] + "."
                    log.save()
                    eleve.ville_etablissement = form.cleaned_data["ville_etablissement"]

                if eleve.classe != form.cleaned_data["classe"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié la classe de l'élève " + eleve.nom + ":" + eleve.classe + " >>> " + form.cleaned_data["classe"] + "."
                    log.save()
                    eleve.classe = form.cleaned_data["classe"]

                if eleve.adresse != form.cleaned_data["adresse"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié l'adresse de l'élève " + eleve.nom + ":" + eleve.adresse + " >>> " + form.cleaned_data["adresse"] + "."
                    log.save()
                    eleve.adresse = form.cleaned_data["adresse"]

                if eleve.code_postale != form.cleaned_data["code_postale"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié le code postale de l'élève " + eleve.nom + ":" + eleve.code_postale + " >>> " + form.cleaned_data["code_postale"] + "."
                    log.save()
                    eleve.code_postale = form.cleaned_data["code_postale"]

                if eleve.nom_responsable_legal != form.cleaned_data["nom_responsable_legal"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié le nom du responsable légal de l'élève " + eleve.nom + ":" + eleve.nom_responsable_legal + " >>> " + form.cleaned_data["nom_responsable_legal"] + "."
                    log.save()
                    eleve.nom_responsable_legal = form.cleaned_data["nom_responsable_legal"]

                if eleve.coordonnees_responsable_legal != form.cleaned_data["coordonnees_responsable_legal"]:
                    log = Log()
                    log.user = request.user.username
                    log.timestamp = datetime.now()
                    log.action = request.user.username + u" a modifié le nom du responsable légal de l'élève " + eleve.nom + ":" + eleve.coordonnees_responsable_legal + " >>> " + form.cleaned_data["coordonnees_responsable_legal"] + "."
                    log.save()
                    eleve.coordonnees_responsable_legal = form.cleaned_data["coordonnees_responsable_legal"]

                eleve.save()

                envoi = True
        else:
            error = True
    else:
        form = Inscription_Eleve(instance = eleve)

    if eleve.nom != '' and eleve.prenom != '' and eleve.date_naissance != None  and eleve.nom_etablissement!= '' :
        if eleve.ville_etablissement != '' and eleve.classe!= '' and eleve.adresse != '' and eleve.code_postale!= '':
            if eleve.nom_responsable_legal != '' and eleve.coordonnees_responsable_legal!= '':
                eleve.inscription_complete = '1'
                eleve.save()

    return render(request, 'inscription/eleve.html', locals())


@login_required
@permission_required('inscription.inscrit')

def autorisations(request,indice):
    equipe = Equipe.objects.get(user__username  = request.user.get_username())
    error = False
    insc = Eleve.objects.get(indice = indice,equipe = equipe)
    eleves = Eleve.objects.filter(equipe = equipe)
    majeur = 0

    if request.method == "POST":
        form = AutorisationsForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data["fiche_sanitaire"] != None:
                log = Log()
                log.user = request.user.username
                log.timestamp = datetime.now()
                log.action = request.user.username + u" a modifié la fiche sanitaire de " + insc.nom + "."
                log.save()
                insc.fiche_sanitaire_version2 = insc.fiche_sanitaire
                insc.fiche_sanitaire = form.cleaned_data["fiche_sanitaire"]

            if form.cleaned_data["autorisation_parentale"] != None:
                log = Log()
                log.user = request.user.username
                log.timestamp = datetime.now()
                log.action = request.user.username + u" a modifié l'autorisation parentale de " + insc.nom + "."
                log.save()
                insc.autorisation_parentale_version2 = insc.autorisation_parentale
                insc.autorisation_parentale  = form.cleaned_data["autorisation_parentale"]

            if form.cleaned_data["autorisation_photo"] != None:
                log = Log()
                log.user = request.user.username
                log.timestamp = datetime.now()
                log.action = request.user.username + u" a modifié l'autorisation photo de " + insc.nom + "."
                log.save()
                insc.autorisation_photo_version2 = insc.autorisation_photo
                insc.autorisation_photo = form.cleaned_data["autorisation_photo"]

            if form.cleaned_data["majeur"]:
                log = Log()
                log.user = request.user.username
                log.timestamp = datetime.now()
                log.action = request.user.username + u" a modifié l'autorisation parentale de " + insc.nom + " (majeur)."
                log.save()
                majeur = 1

            envoi = True
        else:
            error = True
    else:
        form = AutorisationsForm()


    blank_url = "https://s3-eu-west-1.amazonaws.com/tfjm2-inscriptions/media/blank.pdf"
    

    if insc.fiche_sanitaire.url != blank_url and insc.autorisation_photo.url != blank_url:
        if insc.autorisation_parentale.url != blank_url or majeur == 1:
            insc.autorisations_completees = '1'
            insc.save()
    
    insc.save()
    return render(request, 'inscription/autorisations.html', locals())


@login_required
@permission_required('inscription.inscrit')

def problemes(request):
    
    
    blank_url = "https://s3-eu-west-1.amazonaws.com/tfjm2-inscriptions/media/blank.pdf"

    name = request.user.get_username()
    equipe = Equipe.objects.get(user__username  = name)


    tournoi = Tournoi.objects.get(lieu = equipe.tournoi.lieu)


    problemes = Probleme.objects.filter(equipe__nom_equipe=equipe.nom_equipe)

    maxi = 0
    for p in problemes:
        if int(p.version)>maxi:
            maxi = int(p.version)

    maximum = str(maxi)
    mini = 0

    for p in problemes:
        if int(p.version)<maxi:
            mini = int(p.version)

    dico ={}

    problemes1 = Probleme.objects.filter(equipe__nom_equipe=equipe.nom_equipe)

    for p in problemes1:
        key = p.numero+"_version1"
        pbs = Probleme.objects.filter(equipe__nom_equipe=equipe.nom_equipe, numero = p.numero)
        maxi = 0
        for t in pbs:
            if int(t.version)>maxi:
                maxi = int(t.version)
        dico[key] = Probleme.objects.get(equipe__user__username= equipe.user.username, numero = p.numero, version = str(maxi))

    for p in problemes1:
        key = p.numero+"_version2"
        pbs = Probleme.objects.filter(equipe__nom_equipe=equipe.nom_equipe, numero = p.numero)
        mini = 99
        for t in pbs:
            if int(t.version)<mini:
                mini = int(t.version)
        dico[key] = Probleme.objects.get(equipe__user__username= equipe.user.username, numero = p.numero, version = str(mini))

    date_limite = 0
    error = False
    mtn = datetime.now()

    nombre_problemes = int(equipe.tournoi.nombre_problemes)

    probleme_form_set = formset_factory(Probleme_Form, extra=nombre_problemes)


    probleme_accent = 0

    compteur = 0
    if equipe.tournoi.date_limite_def > mtn.date():
        if request.method == "POST":
            formset = probleme_form_set(request.POST, request.FILES)
            if formset.is_valid():
                if probleme_accent == 0:           
                    for form in formset:
                        compteur+=1
                        if form.cleaned_data.get("probleme") != None:
                            key1 = str(compteur)+"_version1"
                            key2 = str(compteur)+"_version2"
                            numero = int(dico[key1].version)
                            if dico[key2].fichier.url != blank_url: 
                                dico[key2].fichier.delete()
                            dico[key2].fichier = dico[key1].fichier
                            dico[key2].version = str(numero)
                            dico[key2].save()
                            dico[key1].fichier = form.cleaned_data.get("probleme")
                            dico[key1].version = str(numero+1)
                            dico[key1].save()
                            log = Log()
                            log.user = request.user.username
                            log.timestamp = datetime.now()
                            log.action = request.user.username + u" a modifié le problème " + str(compteur) + u"de son équipe."
                            log.save()

                envoi = True
            else:
                error = True
        else:
            formset = probleme_form_set()
    else:
        date_limite = 1

    if date_limite == 0:

        liste = {}
        compteur = 0


        for form in formset:
            compteur+=1
            problemes1 = Probleme.objects.filter(equipe__nom_equipe=equipe.nom_equipe, numero = str(compteur))

            maxi = 0
            for p in problemes1:
                if int(p.version)>maxi:
                    maxi = int(p.version)
            chaine1 = str(maxi)
            chaine2 = str(maxi-1)
            liste[compteur] = {(chaine1, chaine2):form}


    return render(request, 'inscription/problemes.html',locals())



def private_ddl(request,equipe,problemes,numero,version,url,filename):
    if Equipe.objects.get(nom_equipe = equipe):
        eq = Equipe.objects.get(nom_equipe = equipe)
        if request.user.username == eq.user.username:
            if problemes == "problemes":
                pb = Probleme.objects.get(equipe__nom_equipe =eq.nom_equipe, numero=numero, version=version)
                url = pb.fichier.url
                filename = eq.trigramme + "_probleme" + pb.numero +"_version" + pb.version

            elif problemes == "fiche_sanitaire":
                if version == '1':
                    eleve = Eleve.objects.get(equipe__nom_equipe =eq.nom_equipe, indice=numero)
                    pb = eleve.fiche_sanitaire
                    url = pb.fichier.url
                    filename = eq.trigramme + "_fiche_sanitaire_" + eleve.nom +"_version1"

                elif version == '2':
                    eleve = Eleve.objects.get(equipe__nom_equipe =eq.nom_equipe, indice=numero)
                    pb = eleve.fiche_sanitaire_version2
                    url = pb.fichier.url
                    filename = eq.trigramme + "_fiche_sanitaire_" + eleve.nom +"_version2"

            elif problemes == "autorisation_photo":
                if version == '1':
                    eleve = Eleve.objects.get(equipe__nom_equipe =eq.nom_equipe, indice=numero)
                    pb = eleve.autorisation_photo
                    url = pb.fichier.url
                    filename = eq.trigramme + "_autorisation_photo_" + eleve.nom +"_version1"

                elif version == '2':
                    eleve = Eleve.objects.get(equipe__nom_equipe =eq.nom_equipe, indice=numero)
                    pb = eleve.autorisation_photo_version2
                    url = pb.fichier.url
                    filename = eq.trigramme + "_autorisation_photo_" + eleve.nom +"_version2"

            elif problemes == "autorisation_parentale":
                if version == '1':
                    eleve = Eleve.objects.get(equipe__nom_equipe =eq.nom_equipe, indice=numero)
                    pb = eleve.autorisation_parentale
                    url = pb.fichier.url
                    filename = eq.trigramme + "_autorisation_parentale_" + eleve.nom +"_version1"

                elif version == '2':
                    eleve = Eleve.objects.get(equipe__nom_equipe =eq.nom_equipe, indice=numero)
                    pb = eleve.autorisation_parentale_version2
                    url = pb.fichier.url
                    filename = eq.trigramme + "_autorisation_parentale_" + eleve.nom +"_version2"

            
            
            excel = urllib.urlopen(url)
            output = StringIO.StringIO(excel.read())
            out_content = output.getvalue()
            output.close()

            response = HttpResponse(out_content,content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % filename
            return response
        else:
            raise Http404
    else:
        raise Http404

def programme(request):
    return render(request,'inscription/programme.html')

def tournoi_information(request):
    return render(request,'inscription/le_tournoi_information.html')

def tournoi_documents(request):
    return render(request,'inscription/le_tournoi_documents_officiels.html')

def faq(request):
    return render(request,'inscription/faq.html')

def jury(request):
    return render(request,'inscription/jury.html')

def liste_des_problemes(request):
    return render(request,'inscription/liste_problemes.html')

def editions_precedentes_participants(request):
    return render(request,'inscription/editions_precedentes_participants.html')

def editions_precedentes_resultats(request):
    return render(request,'inscription/editions_precedentes_resultats.html')

def editions_precedentes_solutions(request):
    return render(request,'inscription/editions_precedentes_solutions_ecrites.html')

def editions_precedentes_photos_et_videos(request):
    return render(request,'inscription/editions_precedentes_photos_et_videos.html')

def temoignages(request):
    return render(request,'inscription/temoignages.html')

def contact(request):
    return render(request,'inscription/contact.html')

def soutenir_partenaires(request):
    return render(request,'inscription/soutenir_partenaires.html')

def soutenir_partenaires_2014(request):
    return render(request,'inscription/soutenir_partenaires.html')

def soutenir_comment(request):
    return render(request,'inscription/soutenir_comment.html')

def presse(request):
    return render(request,'inscription/presse.html')

def itym(request):
    return render(request,'inscription/itym.html')

def concours_photo(request):
    return render(request,'inscription/concours_photo.html')


