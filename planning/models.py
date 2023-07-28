from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.timezone import now

class Congress(models.Model):
    
    name = models.CharField(max_length=100)
    number = models.SmallIntegerField()         #nombre de jour de l'event voir les date en 
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="images",blank=True, null=True) # peut etre utilise page d'acceuil de l'event
    
    def __str__(self):
        return self.name

# Create your models here.
class Day(models.Model):
    congress = models.ForeignKey(Congress, related_name="confs_days", on_delete=models.CASCADE)
    date = models.CharField(primary_key=True, max_length=24) #primary_key=True
    
    def __str__(self):
        return str(self.date)

# Create your models here.
class Room(models.Model):
	congress = models.ForeignKey(Congress, related_name="event_conf_name", on_delete=models.CASCADE)
	#moderator = models.ForeignKey(User, related_name="chat_moderator", on_delete=models.CASCADE , default=1)
	name = models.CharField(max_length=250)
	number = models.SmallIntegerField(default=1)  # numero de la salle pour cle du live
	inprogress = models.CharField(max_length=250, blank=True) # titre presentation en cours dans l'attente
 
	def __str__(self):
		return self.name

# Create your models here.
class Session(models.Model):
    room = models.ForeignKey(Room, related_name="event_conf_room", on_delete=models.CASCADE)
    date = models.ForeignKey(Day, to_field='date', default='self.date', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    order = models.SmallIntegerField(default=1)
    time_start = models.TimeField(default=now, blank=True)
    time_end = models.TimeField(default=now, blank=True)

    def clean(self):
        overlapping_sessions = Session.objects.filter(
            room=self.room,
            date=self.date,
            time_start__lt=self.time_end,
            time_end__gt=self.time_start,
        ).exclude(pk=self.pk)

        if overlapping_sessions.exists():
            raise ValidationError("Cette session se chevauche avec une autre session existante.")

    def __str__(self):
        return self.title
    
class File(models.Model):
    path = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    eof = models.BooleanField()
    on_server = models.BooleanField(default=False, null=True)
    in_room = models.BooleanField(default=False, null=True)

    

class Presentation(models.Model):
	session = models.ForeignKey(Session, related_name="event_conf_name", on_delete=models.CASCADE)
	title = models.CharField(max_length=250, default=".............")
	# author = models.CharField(max_length=100,  default="........d.....")
	duration = models.SmallIntegerField(default=30)
	fichier_pptx = models.OneToOneField(File, on_delete=models.CASCADE, null=True, blank=True)



	def __str__(self):
		return self.title
	

class Intervenant(models.Model):
    def __str__(self):
        return f'{self.nom} {self.prenom}'

    nom = models.fields.CharField(max_length=50)
    prenom = models.fields.CharField(max_length=50)
    logo = models.ImageField(upload_to='', blank=True, null=True)

    def to_json(self):
        return {
            'id': self.id,
            'nom_complet': f'{self.nom} {self.prenom}',
            'logo_url': self.logo.url
        }
          
    
class InterPresent(models.Model):

    def __str__(self):
        return f'{self.id_presentation, "-", self.id_intervenant }'

    id_presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE)
    id_intervenant = models.ForeignKey(Intervenant,null= True, on_delete=models.SET_NULL)