import ftplib as ftp
import os, time

from django.http import JsonResponse
from django.shortcuts import render
from planning.models import File, Intervenant, Presentation, Session

def uploadfile(request):
    relative_path = f"media/presentations/fichiers_importes"
    intervenant_all = Intervenant.objects.all()
    # ? RECUPERATION DES DONNEES DE LA REQUETE
    if request.method == 'POST':  
        file = request.FILES['file'].read()
        fileName= request.POST['filename']
        file_id = request.POST['path']
        end = request.POST['end']
        nextSlice = request.POST['nextSlice']
        aborted = request.POST['aborted']
        id_presta = request.POST['id_presta']

        presta = Presentation.objects.get(id=id_presta)
        

        # print("_________aborted____________", aborted) # ? SI 1 ON SUPPRIME LE FICHIER 
        if file=="" or fileName=="" or file_id=="" or end=="" or nextSlice=="" :
            res = JsonResponse({'data':'Invalid Request....'})
            return res
        else:
            # si fichier existe  chargement par chunk (morceau) cad on a déja commencé le chargement
            if file_id == 'null':
                path = f"media/presentations/fichiers_importes/fichier_{id_presta}.pptx"
                # * CREATION DU REPO PRESTA_IMPORTEES
                try:
                    if not os.path.exists(relative_path):
                        os.mkdir(relative_path)
                except Exception as e:
                    print("Erreur lors de la création du répertoire local:", str(e))
                    
                # * ON ECRIT LES FICHIERS EN LOCAL
                with open(path, 'wb+') as destination:
                    destination.write(file)
               
                FileFolder = File()# ? CREATION DE L'INSTANCE
                FileFolder.path = path
                FileFolder.eof = end
                FileFolder.name = f"fichier_{id_presta}.pptx"
                FileFolder.on_server = False
                FileFolder.save()

                #lien entre le fichier upload et la présentation
                if id_presta != 'null':
                    presta = Presentation.objects.get(id=id_presta)
                    presta.fichier_pptx = FileFolder
                    presta.save()
                    
                # * RAJOUT DE LA CONDITION DE CONNEXION AU SERVEUR
                if int(end):
                    FileFolder.in_room = transfer_file(id_presta, presta.session.room.ip_server)
                    FileFolder.on_server = True
                    FileFolder.save()
                    res = JsonResponse({'data':'Uploaded Successfully...','existingPath': FileFolder.name})
                else:
                    res = JsonResponse({'existingPath': FileFolder.id})
                
                return res
            # ? SI LE FICHIER EXISTE
            else:
                path = 'media/presentations/fichiers_importes/' + file_id
                print("_________ chunked ____________", path, file_id)
                infile = File.objects.get(id=int(file_id) )
                
                
                if  infile.id == int(file_id) and aborted=='1': 
                    print("_________DELETED_________",  file_id)
                    infile.delete()
                    os.remove(infile.path)
                    res = JsonResponse({'data':'Upload Aborted!!', 'existingPath':'Aborted'})
                    return res
                elif infile.id == int(file_id):
                    if not infile.eof:
                        with open(infile.path, 'ab+') as destination: 
                            destination.write(file)
                        
                        if int(end):
                            infile.eof = int(end)
                            infile.in_room = transfer_file(id_presta,presta.session.room.ip_server)
                            infile.on_server = True
                            infile.save()
                            res = JsonResponse({'data':'Uploaded Successfully','existingPath':infile.name, 'status':2 if infile.in_room else 1 })
                        else:
                            res = JsonResponse({'existingPath':file_id})    
                        return res
                    else:
                        res = JsonResponse({'data':'EOF found. Invalid request'})
                        return res
                else:
                    res = JsonResponse({'data':'No such file exists on the file_id'})
                    
                    return res
    return render(request, 'Planning/upload.html', {'intervenant_all':intervenant_all})


#*####################################################################################################################
#*                                             FONCTIONS POUR FTP                                                    #
#*####################################################################################################################

# * DEFINITION DES VARIABLES DE CONNEXION
# host = "10.32.1.58" 
# host = "192.168.1.30"                    # ? ADRESSE IP DU SERVEUR FTP (DE LA MACHINE HOTE)
host = "10.32.1.7"
user = "admin"
password = "webeeconf"
#connect = ftp.ftplib(host, user, password) # ? CONNEXION AU SERVEUR FTP


# * TRANSFERT D'UN FICHIER PPTX
# @param nom_du_fichier matrixé (id_presta), lien d'enregistrement
def transfer_file(id, iphost):
    try:
        server = ftp.FTP()
        server.connect(iphost, 21)
        server.login(user, password)
        print("CONNEXION AU SERVEUR REUSSIE")
        # * VENIR CREER LE DOSSIER POUR LE RANGER DEDANS
        print("CREATION DU REPERTOIRE...")
        salle = "pptx_files" #create_repo(server, id)

        if salle:
            try:
                print("DEBUT DU TRANSFERT...")
                pptxfile = f"media/presentations/fichiers_importes/fichier_{id}.pptx"
                with open(pptxfile, "rb") as fichier: 
                    msg = server.storbinary(f"STOR {salle}/fichier_{id}.pptx", fichier) 
               
                if( int(msg[0:3])==226) :
                    print("Transfert de fichier ok : ")
                    return True
                else :
                    return False
            except Exception as e:
                print("Erreur lors de l'envoi du fichier :", str(e))
                server.quit()
                return False
    except:
        print("ERREUR DE CONNEXION AU SERVEUR")
        return False



















# * CONNEXION
def connection_serv():
    server = ftp.FTP()
    print("CONNEXION AU SERVEUR...")
    try: 
        server.connect(host, 21)
        server.login(user, password)
        print("CONNEXION AU SERVEUR REUSSIE")
        #*########################################
        server.quit()# ? DECONNEXION DU SERVEUR
        print("DECONNEXION DU SERVEUR")
    except ftp.all_errors as error:
        print("ERREUR DE CONNEXION AU SERVEUR")
        print(error)

# * CREATION D'UN REPERTOIRE CIBLE
# @param nom_du_repertoire, lien d'enregistrement
# def create_folder():


def create_repo(server, id_file):
    file_obj = File.objects.filter(id=id_file).first()  # Récupérer l'objet File avec l'ID donné
    if file_obj:
        session = Presentation.objects.filter(fichier_pptx=file_obj).first()  # Récupérer la présentation liée à l'objet File
        if session:
            salle = session.session.room.name  # Récupérer le nom de la salle à partir de la session
            # print("__________SESSION____________", session.session)
            # print("__________SALLE____________", salle)
            try: 
                if not repo_exists(server, salle):
                    server.mkd(salle)
                else:
                    print("Le répertoire existe déjà")
            except Exception as e:
                print("Erreur lors de la création du répertoire :", str(e))
            return salle
    return None  

def repo_exists(server, dossier):
    try:
        liste_fichiers = server.nlst()
        if dossier in liste_fichiers:
            return True
        else:
            return False
    except Exception as e:
        print("Erreur lors de la vérification du dossier :", str(e))
        return False
    
def absolute_path(request):
    if request.method == 'POST':
        file = request.POST.get('name', '')
        if file:
            file_path =  os.path.abspath(file)

            return JsonResponse({'message': 'File path retrieved successfully.', 'file_path': file_path})
        else:
            return JsonResponse({'error': 'Path parameter missing.'})
    else:
        return JsonResponse({'error': 'Invalid request method.'})

    