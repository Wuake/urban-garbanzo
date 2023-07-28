import ftplib as ftp
import os, time

from django.http import JsonResponse
from django.shortcuts import render
from planning.models import File, Intervenant, Presentation, Session

# * FONCTION DECORATRICE POUR UN MEILLEUR FEEDBACK
# ! FAIT PLANTER PARCE QU'ELLE RETOURNE PAS UNE REPONSE HTTP
# def decorator_feedback(func):
#     def wrapper(*args, **kwargs):
#         print("DEBUT DU TELECHARGEMENT")
#         func(*args, **kwargs)
#         print("FIN DU TELECHARGEMENT")
#     return wrapper

#*####################################################################################################################
#*                                             FONCTIONS POUR FTP                                                    #
#*####################################################################################################################

# * DEFINITION DES VARIABLES DE CONNEXION
# host = "10.32.1.58" 
host = "192.168.1.30"                    # ? ADRESSE IP DU SERVEUR FTP (DE LA MACHINE HOTE)
# host = "10.32.1.58"
user = "admin"
password = "admin"
#connect = ftp.ftplib(host, user, password) # ? CONNEXION AU SERVEUR FTP

def uploadfile(request):
    relative_path = f"media/presentations/fichiers_importes"
    intervenant_all = Intervenant.objects.all()
    # ? RECUPERATION DES DONNEES DE LA REQUETE
    if request.method == 'POST':  
        file = request.FILES['file'].read()
        fileName= request.POST['filename']
        existingPath = request.POST['path']
        end = request.POST['end']
        nextSlice = request.POST['nextSlice']
        aborted = request.POST['aborted']
        id_presta = request.POST['id_presta']

        print("____________SIZE______________", len(file))

        if len(file) == 0 or len(file) > 10000000000:
            return JsonResponse({'data':'LA FICHIER EST TROP VOLUMINEUX (MAX 1GO)'})

        # print("_________aborted____________", aborted) # ? SI 1 ON SUPPRIME LE FICHIER 
        if file=="" or fileName=="" or existingPath=="" or end=="" or nextSlice=="" :
            res = JsonResponse({'data':'Invalid Request....'})
            return res
        else:
            # ? SI LE FICHIER N'EXISTE PAS 
            if existingPath == 'null':
                # path = 'media/presentations/' + fileName
                path = 'media/presentations/unamed.pptx'
                path_download = 'media/presentations/fichiers_importes/fichier_.pptx'
                # * CREATION DU REPO PRESTA_IMPORTEES
                try:
                    if not os.path.exists(relative_path):
                        os.mkdir(relative_path)
                except Exception as e:
                    print("Erreur lors de la création du répertoire local:", str(e))
                # * ON ECRIT LES FICHIERS EN LOCAL
                with open(path, 'wb+') as destination:
                    destination.write(file)
                with open(path_download, 'wb+') as destination:
                    destination.write(file)
                FileFolder = File()# ? CREATION DE L'INSTANCE
                # FileFolder.existingPath = path
                FileFolder.path = path
                FileFolder.eof = end
                FileFolder.name = "unamed.pptx"
                FileFolder.on_server = True
                FileFolder.save()

                # ? RENOMMAGE DU FICHIER SUR LE SERVEUR
                file = File.objects.get(name="unamed.pptx")
                file.name = f"fichier_{file.id}.pptx"
                # ! SI JE CHANGE LE PATH ON PEUT PLUS TESTER LE FICHIER EN LOCAL
                file.path = f"media/presentations/fichiers_importes/fichier_{file.id}.pptx"
                file.existingPath = f"media/presentations/fichier_{file.id}.pptx" # * PAS SUR D'EN AVOIR BESOIN
                file.save()
                # ? ET DU FICHIER LOCAL
                os.rename(path_download, f"media/presentations/fichiers_importes/fichier_{file.id}.pptx"  )

                #lien entre le fichier upload et la présentation
                if id_presta != 'null':
                    presta = Presentation.objects.get(id=id_presta)
                    presta.fichier_pptx = FileFolder
                    presta.save()
                    print(presta.fichier_pptx.path)

                if int(end):
                    res = JsonResponse({'data':'Uploaded Successfully...','existingPath': fileName})
                else:
                    res = JsonResponse({'existingPath': fileName})
                # print("FILENAME : ", f"fichier_{file.id}.pptx")
                file = File.objects.get(name=f"fichier_{file.id}.pptx")
                transfer_file(file.id)
                return res
            # ? SI LE FICHIER EXISTE
            else:
                path = 'media/presentations/' + existingPath
                #print("_________aborted____________", path, existingPath)
                model_id = File.objects.get(existingPath=path)
                
                if  model_id.name == fileName and aborted=='1': 
                    print("_________DELETED_________",  existingPath)
                    model_id.delete()
                    os.remove(path)
                    res = JsonResponse({'data':'Upload Aborted!!', 'existingPath':'Aborted'})
                    return res
                elif model_id.name == fileName:
                    if not model_id.eof:
                        with open(path, 'ab+') as destination: 
                            destination.write(file)
                        if int(end):
                            model_id.eof = int(end)
                            model_id.save()
                            res = JsonResponse({'data':'Uploaded Successfully','existingPath':model_id.existingPath})
                        else:
                            res = JsonResponse({'existingPath':model_id.name})    
                        return res
                    else:
                        res = JsonResponse({'data':'EOF found. Invalid request'})
                        return res
                else:
                    res = JsonResponse({'data':'No such file exists in the existingPath'})
                    print("__________TRANSFERT EN COURS___________")
                    file = File.objects.get(name=fileName)
                    transfer_file(file.id)
                    return res
    return render(request, 'Planning/upload.html', {'intervenant_all':intervenant_all})


# * CONNEXION
# def connection():
#     server = ftp.FTP()
#     print("CONNEXION AU SERVEUR...")
#     try: 
#         server.connect(host, 21)
#         server.login(usr, password)
#         print("CONNEXION AU SERVEUR REUSSIE")
#         # * appeller les différentes fonctions ici
#         #*########################################
#         server.dir() # ? AFFICHE LE CONTENU DU REPERTOIRE, PAS BESSOIN DE PRINT
#         server.mkd("Salle_2")  
#         send_file(server, "media/presentations/")
#         #*########################################
#         server.quit()# ? DECONNEXION DU SERVEUR
#         print("DECONNEXION DU SERVEUR")
#     except ftp.all_errors as error:
#         print("ERREUR DE CONNEXION AU SERVEUR")
#         print(error)

# * CREATION D'UN REPERTOIRE CIBLE
# @param nom_du_repertoire, lien d'enregistrement
# def create_folder():

# * TRANSFERT D'UN FICHIER PPTX
# @param nom_du_fichier matrixé (id_presta), lien d'enregistrement
def transfer_file(id):
    try:
        server = ftp.FTP()
        server.connect(host, 21)
        server.login(user, password)
        print("CONNEXION AU SERVEUR REUSSIE")
        # * VENIR CREER LE DOSSIER POUR LE RANGER DEDANS
        print("CREATION DU REPERTOIRE...")
        salle = create_repo(server, id)

        if salle:
            try:
                print("DEBUT DU TRANSFERT...")
                with open("media/presentations/unamed.pptx", "rb") as fichier: # ? LIEN DU FICHIER QU'ON VEUT ENVOYER
                    server.storbinary(f"STOR {salle}/fichier_{id}.pptx", fichier) # ? NOM QU'ON LUI DONNE SUR LE SERVEUR
                server.quit()
                print("TRANSFERT DU FICHIER REUSSI")
            except Exception as e:
                print("Erreur lors de l'envoi du fichier :", str(e))
                server.quit()
    except:
        print("ERREUR DE CONNEXION AU SERVEUR")
    
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

    