from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
#from django.contrib.auth.decorators import login_required
from django.http import Http404

import socket
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.http.response import JsonResponse
from django.contrib import messages
#from django.contrib.auth.decorators import user_passes_test
from datetime import date, timedelta, datetime
from django.core.files.base import ContentFile
import base64
import json, os, ftplib as ftp
import datetime as datetime2
# Create your views here.

from .models import *
from .forms import CongressForm, SessionForm, PresentationForm, IntervenantForm

congres_id= 1
def addOneRoom(new):
    # * Si il y a plusieurs congres,
    # * mettre à jour cette fonction qui va chercher le dernier congres créé
    try:
        # * premier élément du QuerySet retourné 
        new = Congress.objects.all().order_by('-id')[0]
    except Congress.DoesNotExist:
        new = None
    if new :
        rooms = Room.objects.all()
        Room.objects.create(congress= new , number=str(rooms.count()+1), name="Salle "+str(rooms.count()+1))
        status = "salle ajoutée"
    else :
        #retournement d'erreur
        print("erreur lors de la creation de la salle => pas de congres en cours")
        status = "error de creation de la salle => pas de congres en cours"

    return JsonResponse({'status': status})


def addRooms(new, nb):
    i=1
    while i <= int(nb) :
        Room.objects.create(congress= new , number=str(i), name="Salle "+str(i))
        i = i+1
        
def addDay(new,date1, date2):
    delta = timedelta(days=1)
    while date1 <= date2:
        #print(date1, date1.strftime("%Y-%m-%d"))
        Day.objects.create(congress= new,date=date1) 
        date1 += delta       
        
    
#selection de la presentation en cours pour affichage dans le live
#@user_passes_test(lambda u: u.is_superuser)
def addcongres(request):
    if request.method == "POST":
        add_form = CongressForm(request.POST,request.FILES)
        if add_form.is_valid():
            id = add_form.cleaned_data['id']
            label = add_form.cleaned_data['label']
            number = add_form.cleaned_data['number']
            description = add_form.cleaned_data['description']
            thumbnail = add_form.cleaned_data['thumbnail']
            date1 = add_form.cleaned_data['date1']
            date2 = add_form.cleaned_data['date2']
            try:
                new = Congress.objects.get(id=id)
            except Congress.DoesNotExist:
                new = None           
            #new, created = Video.objects.get_or_create(id=id, defaults={'title':title, 'name':name, 'body':body, 'thumbnail':thumbnail } )
            if new :
                new.name=label
                new.description=description
                new.thumbnail=thumbnail
                new.save()
            else :
                new = Congress.objects.create(name=label, number=number, description=description, thumbnail=thumbnail)
                addRooms(new, number)
                addDay(new, datetime.strptime(date1, '%Y-%m-%d').date(), datetime.strptime(date2, '%Y-%m-%d').date() )
           
            
            messages.success(request,'Un nouveau congrès a été crée : '+ add_form['label'].value())
            return redirect( "planning:home" )
        else : messages.error(request,'Formulaire invalide : '+add_form.errors)
       
    # si modification
    idCongres = request.GET.get('id')
    if idCongres :
        cg =Congress.objects.get(id=idCongres)
        days = Day.objects.filter(congress=cg)
        print(days[0], days[1])
        form = CongressForm(initial={'id': cg.id, 'label': cg.name, 'description': cg.description, 'thumbnail': cg.thumbnail, 'number': cg.number, "date1":days[0], "date2":days[1]})
    else :
        form = CongressForm()
        print("id congres ===== ", idCongres)
    
    return render(request, "Planning/congres.html", {"add_form":form}) 


def home(request):
    idCongres = request.GET.get('id')
    if idCongres :
        global congres_id
        cg = Congress.objects.get(id=idCongres) 
        congres_id = idCongres
        
        return redirect( "planning:create" )
    else :
        congress = Congress.objects.all()
        
        context = {
            'congress': congress,
            'congres_id': congres_id,
        }
        
    return render(request, "Planning/home.html", context) 

# mise a jour de la presentation en cours dans le champ dedié de la room pour affichage dans le live
#@user_passes_test(lambda u: u.is_superuser)
def create(request):
    congres = Congress.objects.get(id=congres_id)
    
    rooms = Room.objects.filter(congress__pk=congres.pk)
    days = Day.objects.filter(congress__pk=congres.pk)
    request.session["congres_name"] = congres.name
    pform = PresentationForm(congress_id =congres_id)
    sform = SessionForm()
    return render(request, "Planning/create.html", {"congres_name":congres.name, 'rooms': rooms,'days': days,"sess_form":sform, "pres_form":pform}) 


def show_plan(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # print("coucou1")

        date = request.POST.get('date')

        # Récupérer les sessions pour la date sélectionnée
        day = get_object_or_404(Day, date=date)
        sessions = Session.objects.filter(date=day).order_by('time_start')

        # Créer des listes pour stocker les données des sessions
        session_data = {}
        start_times = {}
        end_times = {}
        print()
        minheure = "07:00:00"
        maxheure = "21:00:00"
        print("---------------Horraire de base-------------------")
        print(minheure)
        print(maxheure)

        for session in sessions:
            room_name = session.room.name
            session_title = session.title
            session_starttime = session.time_start.strftime('%H:%M:%S')
            session_endtime = session.time_end.strftime('%H:%M:%S')

            
            print("---------------Session start et end-------------------")
            print(session_starttime)
            print(session_endtime)

            if session_starttime < minheure:
                minheure = session_starttime
            if session_endtime > maxheure:
                maxheure = session_starttime

            print("---------------Horraire min et max-------------------")
            print(minheure)
            print(maxheure)

            if room_name in session_data:
                session_data[room_name].append(session_title)
                start_times[room_name].append(session_starttime)
                end_times[room_name].append(session_endtime)
            else:
                session_data[room_name] = [session_title]
                start_times[room_name] = [session_starttime]
                end_times[room_name] = [session_endtime]

        # Exemple de réponse JSON avec les données des sessions et les horaires de début/fin
        data = {
            'sessions': session_data,
            'start_times': start_times,
            'end_times': end_times,
            'min_heure': minheure,
            'max_heure': maxheure
        }

        return JsonResponse(data)
    else:
        congress = Congress.objects.get(id=congres_id)
        days = Day.objects.filter(congress__pk=congress.pk)
        rooms = Room.objects.all()
        print("coucou2")
        context = {'congress': congress, 'days': days, 'rooms': rooms}
        return render(request, 'Planning/show.html', context)
    
def planning_plan(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # print("coucou1")

        date = request.POST.get('date')

        # Récupérer les sessions pour la date sélectionnée
        day = get_object_or_404(Day, date=date)
        sessions = Session.objects.filter(date=day).order_by('time_start')

        # Créer des listes pour stocker les données des sessions
        session_data = {}
        start_times = {}
        end_times = {}
        print()
        minheure = "07:00:00"
        maxheure = "21:00:00"
        heurechangenumber = 0
        # print("---------------Horraire de base-------------------")
        # print(minheure)
        # print(maxheure)

        for session in sessions:
            room_name = session.room.name
            session_title = session.title
            session_starttime = session.time_start.strftime('%H:%M:%S')
            session_endtime = session.time_end.strftime('%H:%M:%S')

            
            # print("---------------Session start et end-------------------")
            # print(session_starttime)
            # print(session_endtime)

            minheure_dt = datetime2.datetime.strptime(minheure, '%H:%M:%S').time()
            maxheure_dt = datetime2.datetime.strptime(maxheure, '%H:%M:%S').time()
            session_starttime_dt = datetime2.datetime.strptime(session_starttime, '%H:%M:%S').time()
            session_endtime_dt = datetime2.datetime.strptime(session_endtime, '%H:%M:%S').time()

            if session_starttime_dt < minheure_dt:
                time_diff = datetime2.datetime.combine(datetime2.date.today(), session_starttime_dt) - datetime2.datetime.combine(datetime2.date.today(), minheure_dt)
                hours_diff = round(time_diff.total_seconds() / 3600)
                minheure = session_starttime
                heurechangenumber -= hours_diff
            # print(heurechangenumber)

            if session_endtime_dt > maxheure_dt:
                time_diff = datetime2.datetime.combine(datetime2.date.today(), session_endtime_dt) - datetime2.datetime.combine(datetime2.date.today(), maxheure_dt)
                hours_diff = round(time_diff.total_seconds() / 3600)
                maxheure = session_endtime
                heurechangenumber -= hours_diff

            # print("---------------Horraire min et max-------------------")
            # print(minheure)
            # print(maxheure)

            if room_name in session_data:
                session_data[room_name].append(session_title)
                start_times[room_name].append(session_starttime)
                end_times[room_name].append(session_endtime)
            else:
                session_data[room_name] = [session_title]
                start_times[room_name] = [session_starttime]
                end_times[room_name] = [session_endtime]

        # Exemple de réponse JSON avec les données des sessions et les horaires de début/fin
        data = {
            'sessions': session_data,
            'start_times': start_times,
            'end_times': end_times,
            'min_heure': minheure,
            'max_heure': maxheure,
            'heurechangenumber': heurechangenumber
        }

        return JsonResponse(data)
    else:
        congress = Congress.objects.get(id=congres_id)
        days = Day.objects.filter(congress=congress)
        rooms = Room.objects.filter(congress=congress)
        context = {'congress': congress, 'days': days, 'rooms': rooms}
        return render(request, 'Planning/planning.html', context)
    

def show_pupitre(request):
    congres = Congress.objects.get(id=congres_id)
    rooms = Room.objects.filter(congress__pk=congres.pk)
    days = Day.objects.filter(congress__pk=congres.pk)
    pform = PresentationForm(congress_id =congres_id)
    sform = SessionForm()
    return render(request, "Planning/pupitre.html", {'rooms': rooms,'days': days,"sess_form":sform, "pres_form":pform}) 

def add_speaker(request):
    
    if request.method == 'POST':
             
        form = IntervenantForm()
        form = IntervenantForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data 
        else :    
            response = {'success': False, 'form non valid ': form.errors}
            return JsonResponse(response)
        
        try:
            speaker = Intervenant.objects.get(id=int(cd['id']))
        except Intervenant.DoesNotExist:
            speaker = None

        if speaker is None:
            congres = Congress.objects.get(id=congres_id)
            speaker = Intervenant(
                nom = cd['nom'],
                prenom = cd['prenom'],
                logo = cd['logo'],
                congress=congres
            )     
            speaker.save() 
           
        else:
            speaker.nom=cd['nom']
            speaker.prenom=cd['prenom']
            speaker.logo=cd['logo']
            speaker.save()

        if speaker :
            response = {'success': True, 'speaker': speaker.to_json()}
        else:
            response = {'success': False, 'errors': form.errors}
            
        return JsonResponse(response)
    else:
        intervenants = Intervenant.objects.filter(congress__id=congres_id)
        Intervenant_form = IntervenantForm()
        
        context = {
            'intervenants': intervenants,
            'Intervenant_form': Intervenant_form
        }
        
        return render(request, 'Planning/intervenant.html', context)    

def delete_intervenant(request, intervenant_id):
    try:
        intervenant = Intervenant.objects.get(id=intervenant_id)
        intervenant.delete()
        return JsonResponse({'success': True})
    
    except Intervenant.DoesNotExist:
        return JsonResponse({'success': False, 'errors': 'Intervenant does not exist.'})


"""
#@login_required
def ajax_load_planning(request, pk, date):
    today = date
    #today = '2023-04-18'
    presentations = Presentation.objects.select_related('session').filter(session__room_id=pk, session__date=today)
	
	#print(presentations.query)
    presentations_list = [{
        "id": presentation.pk,
        "title": presentation.title,
        "author": presentation.author,
        "duration": presentation.duration,
        "session_id": presentation.session_id,
        "session_title": presentation.session.title,
        "time_begin": presentation.session.time_start,
        "time_end": presentation.session.time_end,
    } for presentation in presentations ]
    
    return JsonResponse(presentations_list, safe=False)
"""

def ajax_load_planning(request, pk, date):
    today = date
    presentations = Presentation.objects.select_related('session').filter(session__room_id=pk, session__date_id=date)

    presentations_list = []
    for presentation in presentations:
        interpresents = InterPresent.objects.filter(id_presentation=presentation.pk)
        inter_list = []
        infos = []
        infos_id = []
        print(interpresents)
        #on itere sur les interpresent
        for interp in interpresents:
            # print(interp.id_intervenant)
            # infos_id.append(interp.id_intervenant.id)
            # print(infos_id)
            # print(interp.id_intervenant.id)
            inter_dict = {
                'id': interp.id_intervenant.id,
                'nom': interp.id_intervenant.nom,
                'prenom': interp.id_intervenant.prenom
            }   
            inter_list.append(inter_dict)

        #On met le tout dans un tableau pour afficher les différents noms et prenoms des gens qui ont une présentation
        for personne in inter_list:
            # print(personne)
            infos.append(" " + personne['nom'] + " " + personne['prenom'])
            infos_id.append(personne['id'])
        # print(infos_id)

        # print(infos)
        if presentation.fichier_pptx :
            isFile =True
        else :
            isFile = False
        presentation_dict = {
            "id": presentation.pk,
            "title": presentation.title,
            "author": infos,
            "author_id": infos_id,  
            "duration": presentation.duration,
            "session_id": presentation.session_id,
            "session_title": presentation.session.title,
            "time_begin": presentation.session.time_start.strftime('%H:%M'),
            "time_end": presentation.session.time_end.strftime('%H:%M'),
            "fichier_pptx" : isFile,
        }
        # print(presentation.session.time_start.strftime('%H:%M'), presentation.session.time_end.strftime('%H:%M'))
        presentations_list.append(presentation_dict)

    return JsonResponse(presentations_list, safe=False)


# * charge les salles d'un congres
# * prend en param l'id du congres
def ajax_load_rooms(request):
    # retire la ligne là si y'a plusieurs congrès et passe en param le pk du congrès visé
    pk = Congress.objects.all().order_by('-id')[0]
    rooms = Room.objects.filter(congress__pk=pk.id)
    rooms_list = [{
        "id": room.pk,
        "name": room.name,
        "congress": room.congress.name,
        "number": room.number,
    } for room in rooms]
    print("Salut à tous c'est la salle")
    return JsonResponse(rooms_list, safe=False)


#@login_required
def ajax_add_session(request, pk):
    response_data = {}
    today = date.today()
    if request.method == 'POST':
        jsonbody = json.loads(request.body)
        # print("_________________________________________________________", jsonbody['id'],  jsonbody['title'])
        try:
            new = Session.objects.get(id=int(jsonbody['id']))
        except Session.DoesNotExist:
            new = None

        if new is None:
            start_time = datetime.strptime(jsonbody['time1'], '%H:%M').time()
            end_time = datetime.strptime(jsonbody['time2'], '%H:%M').time()
            date_id = jsonbody['dateid']
            #existing_sessions = Session.objects.filter(  Q(room_id=pk) & Q(date_id=date_id) &  (Q(time_start__lt=end_time) & Q(time_end__gt=start_time)) )
            
            if False : #existing_sessions.exists():
                response_data['error'] = 'Une session existe déjà à ce moment-là'
            else:
                sess = Session.objects.create(
                    room_id=pk,
                    date_id=date_id,
                    title=jsonbody['title'],
                    time_start=start_time,
                    time_end=end_time
                )
                if sess:
                    Presentation.objects.create(
                        session_id=sess.id,
                        title='Présentation',
                        duration=30,
                    )
                response_data['success'] = 'Session créée avec succès'
        else:
            start_time = datetime.strptime(jsonbody['time1'], '%H:%M').time()
            end_time = datetime.strptime(jsonbody['time2'], '%H:%M').time()
            date_id = jsonbody['dateid']
            #existing_sessions = Session.objects.filter( Q(room_id=pk) & Q(date_id=date_id) & ~Q(id=new.id) & (Q(time_start__lt=end_time) & Q(time_end__gt=start_time)))
            #if existing_sessions.exists():
             #   response_data['error'] = 'Une session existe déjà à ce moment-là'
            #else:
            new.title = jsonbody['title']
            new.time_start = start_time
            new.time_end = end_time
            new.save()
            response_data['success'] = 'Session mise à jour avec succès'
               

    presentations_list = {}
    return JsonResponse(response_data, safe=False)

"""
def ajax_add_intervenant(request, pk):
    response_data = {}
    today = date.today()
    
    if request.method == 'POST':
        jsonbody = json.loads(request.body)
        # print("_________________________________________________________", jsonbody['id'],  jsonbody['title'])
        try:
            new = Session.objects.get(id=int(jsonbody['id']))
        except Session.DoesNotExist:
            new = None

        if new is None:
            start_time = datetime.strptime(jsonbody['time1'], '%H:%M').time()
            end_time = datetime.strptime(jsonbody['time2'], '%H:%M').time()
            date_id = jsonbody['date']
            existing_sessions = Session.objects.filter(
                Q(room_id=pk) & Q(date_id=date_id) &
                (Q(time_start__lt=end_time) & Q(time_end__gt=start_time))
            )
            if existing_sessions.exists():
                response_data['error'] = 'Une session existe déjà à ce moment-là'
            else:
                sess = Session.objects.create(
                    room_id=pk,
                    date_id=date_id,
                    title=jsonbody['title'],
                    time_start=start_time,
                    time_end=end_time
                )
                if sess:
                    Presentation.objects.create(
                        session_id=sess.id,
                        title='Présentation',
                        duration=30,
                    )
                response_data['success'] = 'Session créée avec succès'
        else:
            start_time = datetime.strptime(jsonbody['time1'], '%H:%M').time()
            end_time = datetime.strptime(jsonbody['time2'], '%H:%M').time()
            date_id = jsonbody['date']
            existing_sessions = Session.objects.filter(
                Q(room_id=pk) & Q(date_id=date_id) & ~Q(id=new.id) &
                (Q(time_start__lt=end_time) & Q(time_end__gt=start_time))
            )
            if existing_sessions.exists():
                response_data['error'] = 'Une session existe déjà à ce moment-là'
            else:
                new.title = jsonbody['title']
                new.time_start = start_time
                new.time_end = end_time
                new.save()
                response_data['success'] = 'Session mise à jour avec succès'

    presentations_list = {}
    return JsonResponse(response_data, safe=False)
"""
#@login_required
def ajax_add_pres(request, pk):
    #posts = Post.objects.all()
    response_data = {}
    today = date.today()
    if request.method == 'POST':
        jsonbody = json.loads(request.body)

        response_data['title'] = jsonbody['title']
        response_data['time2'] = jsonbody['duration']
        response_data['author'] = jsonbody['author']
        response_data['author1'] = jsonbody['author1']
        response_data['author2'] = jsonbody['author2']

        # ! REGLER LE BUG DE MODIFICATION DES INFORMATIONS DE PRESENTATION
        try:
            new = Presentation.objects.get(id=int(jsonbody['id']))   
        except Presentation.DoesNotExist:
            new = None           
            
        if new :           
            new.session_id = pk
            new.title=jsonbody['title']
            new.duration=jsonbody['duration']
            new.save()
        
        else :

            new =  Presentation.objects.create( session_id = pk,
                                                title = jsonbody['title'],
                                                # author= jsonbody['author'],
                                                duration= jsonbody['duration'],
                                                )
           
        #  supprime tous les auteurs et on ajoute les nouveaux
        InterPresent.objects.filter(id_presentation=new).delete()
                  
        if(jsonbody['author']):
            new_intervenant = Intervenant.objects.get(id=int(jsonbody['author']))
            if new_intervenant :
                InterPresent.objects.create( id_presentation = new, id_intervenant = new_intervenant )
        if(jsonbody['author1']):
            new_intervenant1 = Intervenant.objects.get(id=int(jsonbody['author1'])) 
            if new_intervenant1 :
                InterPresent.objects.create( id_presentation = new, id_intervenant = new_intervenant1 )       
        if(jsonbody['author2']):
            new_intervenant2 = Intervenant.objects.get(id=int(jsonbody['author2']))
            if new_intervenant2 :
                InterPresent.objects.create( id_presentation = new, id_intervenant = new_intervenant2 )     
          
            
    return JsonResponse(response_data, safe=False)

#@user_passes_test(lambda u: u.is_superuser)
def ajax_del_pres(request, pk):
    if request.method == 'POST':
        jsonbody = json.loads(request.body)
        
        if jsonbody['is_sess'] == 1 :
            Session.objects.filter(id=pk).delete()
        else : 
            Presentation.objects.filter(id=pk).delete()
    
    return JsonResponse({}, safe=False)

# open pptx file on server
def open_ppt(host, ppt_file):
    host = host
    port = 5000
    message = f"open_ppt@{ppt_file}".encode()
    # create socket
    try :
        sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error  :
        print ('Failed to create socket. Error code: ' + socket.error)
        return False
   
    try :
        sock.connect((host, port))
        sock.sendall(message)
        # get server response
        response = sock.recv(1024)
        # decode the response and return it
        print ( response.decode )
        return response.decode()
    except socket.error as msg :
       
        return "Erreur de connexion au serveur pptx : "+str(msg)
# open pptx file on server      
def ouvrir_presentation(request):

    data = json.loads(request.body)
    id_pres = data.get('id', '') 
    room_ip = data.get('room_ip', '')
    presentation = Presentation.objects.get(id=id_pres)
    # print(presentation)
    fichier_pptx = presentation.fichier_pptx
    print("le fichier =>" + fichier_pptx.name)
    print("Voici le lien vers le fichier =>" + fichier_pptx.path)

    response = open_ppt(room_ip, fichier_pptx.name)
    
    return JsonResponse({"message": response})



def show_upload(request):
    intervenant_all = Intervenant.objects.filter(congress__id=congres_id)

    return render(request, 'Planning/upload.html', {'intervenant_all': intervenant_all})

def intervenant_select(request):

    data = json.loads(request.body)
    id = data.get('id', '')

    print(id)
    presentations = Presentation.objects.filter(interpresent__id_intervenant=id)
    presentation_list = []

    for presentation in presentations:
        presentation_list.append({
            'id': presentation.id,
            'title': presentation.title,
            'duration': presentation.duration,
            'fichier_pptx': presentation.fichier_pptx.path if presentation.fichier_pptx else None,
            'on_server' : presentation.fichier_pptx.on_server if presentation.fichier_pptx else False,
            'in_room' : presentation.fichier_pptx.in_room if presentation.fichier_pptx else False
            
        })

    # print(presentation_list)
    
    return JsonResponse({"presentations": presentation_list})

def upload_file(request):
    file = request.FILES.get("file")

    # fss = FileSystemStorage()
    # filename = fss.save(file.name, file)
    # url = fss.url(filename)
    print(file)
    data = ContentFile(base64.b64decode(file), name=file.name) 
    Presentation.objects.create(doc=data)
    print(data)
    return JsonResponse({"link": data})


# * CHAQUE PC A UNE SEULE SALLE ATTRIBUEE A TRAVERS TOUS LES CONGRES
# ! UNE SEUL PROGRAMME TOURNE DONC SOUCIS
# * ON VA TOUT CHERCHER D'UN COUP POUR LE MOMENT
def fetching_files(request):
    # * ADDRESSE DU PC SERVEUR
    host = "127.0.0.1"
    # host = "192.168.1.30"
    user = "admin"
    password = "webeeconf"
    message=''
    allok=True

    if request.method == 'POST':  
        host = json.loads(request.body).get('room_ip', '')
        room_id = json.loads(request.body).get('room_id', '')
        print(host, room_id)
       
        files = []
        try:
            print("CONNEXION AU SERVEUR...")
            server = ftp.FTP()
            server.connect(host, 21)
            server.login(user, password)

            try:
                print("DEBUT DU TRANSFERT...")
                press = Presentation.objects.filter(session__room__id=room_id)
                for pres in press:
                    file = pres.fichier_pptx
                    
                    if file and not file.in_room : 
                        print("tranfert file  ",  file.path)
                        pptxfile = f"media/presentations/fichiers_importes/fichier_{pres.id}.pptx"
                        with open(file.path, "rb") as fichier: 
                            msg = server.storbinary(f"STOR pptx_files/{file.name}", fichier) 
                
                            if( int(msg[0:3])==226) :
                                print("Envoi du fichier OK ", msg)
                                file.in_room = True
                                file.save()
                                #return True
                            else :
                                file.in_room = False
                                file.save()
                            
            except Exception as e:
                print("Erreur lors de l'envoi du fichier :", str(e))
                message = "Erreur lors de l'envoi du fichier : "+str(e)
            
            server.quit()
        except Exception as e:
            print("Erreur lors de l'envoi du fichier :", str(e))
            return JsonResponse({"message": 'Erreur connexion au serveur ftp!'})  
        
    return JsonResponse({"message": message, "allok":allok})




# * CHANGE LA COULEUR DU BOUTON PLAY EN FONCTION DE L'IMPORT DU FICHIER
def couleur_bouton(request):
    id = json.loads(request.body).get('id', '')
    # * on veut savoir pour un seul fichier
    fichier = File.objects.filter(id = id)

    serv = True if fichier.on_serveur else False
    laptop = True if fichier.on_laptop else False
    # * 0 = pas de fichier, 1 = fichier sur serveur, 2 = fichier sur laptop & serveur
    res = 1 if serv and not laptop else 2 if serv and laptop else 0

    return JsonResponse({"status": res})

def pupitre_trigger(request):
    files = File.objects.all()
    for file in files:
        if file.on_server:
            file.in_room = True
            file.save()
    return JsonResponse({"success": True})