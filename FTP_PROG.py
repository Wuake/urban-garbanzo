# 
# * PROGRAMME PYTHON QUI PERMET LE TRANSFERT DE FICHIER EN FTP
# * sdz.tdct.org/sdz/utiliser-le-module-ftp-de-python.html

# * IMPORTATION DES MODULES
import ftplib as ftp

# * DEFINITION DES VARIABLES DE CONNEXION
host = "192.168.0.119"                     # ? ADRESSE IP DU SERVEUR FTP (DE LA MACHINE HOTE)
user = "admin"
password = "admin"
connect = ftp.ftplib(host, user, password) # ? CONNEXION AU SERVEUR FTP

# * ENVOI D'UN FICHIER
ftp_file = "C:\Users\samy\Desktop\lien_vers_le_fichier_.py"
file_to_send = open(ftp_file, "rb")                  # ? OUVERTURE DU FICHIER 
connect.storbinary("STOR " + ftp_file, file_to_send) # ? ENVOI DU FICHIER SUR LE SERVEUR FTP
file_to_send.close()                                 # ? FERMETURE DU FICHIER

# * ETAT DE LA CONNEXION
state = connect.getwelcome()            # ? RECUPERATION DU MESSAGE DE BIENVENUE
print("Etat de la connexion : ", state) # ? AFFICHAGE DU MESSAGE DE BIENVENUE

# * RECUPERATION DU DOSSIER
repo = connect.dir()                    # ? RECUPERATION DU CONTENU DU DOSSIER
print("Contenu du dossier : ", repo)

# * RENOMER UN FICHIER OU UN DOSSIER
rename = raw_input("Quel fichier voulez-vous renommer : ")
new_name = raw_input("Quel est le nouveau nom : ")
connect.rename(rename, new_name)        # ? RENOME LE FICHIER OU LE DOSSIER

# * SUPPRIMER UN FICHIER
delete = raw_input("Quel fichier voulez-vous supprimer : ")
connect.delete(delete)                  # ? SUPPRIME LE FICHIER OU LE DOSSIER

# * CREER UN DOSSIER
new_repo = raw_input("Quel est le nom du nouveau dossier : ")
connect.mkd(new_repo)                   # ? CREE UN NOUVEAU DOSSIER

# * SUPPRIMER UN DOSSIER
delete_repo = raw_input("Quel dossier voulez-vous supprimer : ")
connect.rmd(delete_repo)                # ? SUPPRIME LE DOSSIER

# * ENVOYER UNE COMMANDE AU SERVEUR
command = raw_input("Quelle commande voulez-vous envoyer : ")
connect.sendcmd(command)                # ? ENVOI LA COMMANDE AU SERVEUR

# ? FERMETURE DE LA CONNEXION
connect.quit()