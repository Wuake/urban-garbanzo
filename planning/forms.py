from planning.models import Congress, InterPresent, Intervenant, Presentation

from django import forms

       
class CongressForm(forms.Form):
    id = forms.CharField(label='', initial=-1,widget=forms.TextInput(attrs={'type': 'hidden', 'id':"cong_id"}) )
    label = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'label', 'id':"cong_label"}) )
    description = forms.CharField(label='', widget=forms.Textarea( attrs={"rows":"4", 'placeholder': 'Description..', 'id':"vid_body"} ))
    thumbnail = forms.ImageField(label='', required=True, widget=forms.FileInput(attrs={'placeholder': 'Vignette de la vidéo', 'id':"vid_thumb"}) )
    number = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'Nombre de salles', 'id':"cong_number"}) )  
    date1 = forms.CharField(label='',widget=forms.DateInput(attrs={'type': 'date','placeholder': 'Date de début', 'id':"date1"}) ) 
    date2 = forms.CharField(label='',widget=forms.DateInput(attrs={'type': 'date','placeholder': 'Date de fin', 'id':"date2"}) ) 
    
class SessionForm(forms.Form):
    id = forms.CharField(label='', initial=-1,widget=forms.TextInput(attrs={'type': 'hidden', 'id':"sess_id"}) )
    name = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'Nom de session', 'id':"sess_name"}) )
    date1 = forms.CharField(label='',widget=forms.TimeInput(attrs={'type': 'time','format':'%H:%M','placeholder': 'Heure de début', 'id':"sess_time1"}) ) 
    date2 = forms.CharField(label='',widget=forms.TimeInput(attrs={'type': 'time','format':'%H:%M','placeholder': 'Heure de fin', 'id':"sess_time2"}) ) 

class PresentationForm(forms.Form):
        congres=1
     #overwrite __init__
        def __init__(self,congress_id):
            # call standard __init__
            congres = congress_id
            super().__init__()
              
        id = forms.CharField(label='', initial=-1,widget=forms.TextInput(attrs={'type': 'hidden', 'id':"pres_id"}) )
        name = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'Titre de la présentation', 'id':"pres_name"}) )
        duration = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'Durée de la présentation', 'id':"pres_duration"}) )
        author = forms.ModelChoiceField(queryset=Intervenant.objects.filter(congress__id=1), label='',widget=forms.Select(attrs={'placeholder': 'Auteurs', 'id':"pres_author"}) )
        author1 = forms.ModelChoiceField(queryset=Intervenant.objects.filter(congress__id=1), label='',widget=forms.Select(attrs={'placeholder': 'Auteurs', 'id':"pres_author1"}) )
        author2 = forms.ModelChoiceField(queryset=Intervenant.objects.filter(congress__id=1), label='',widget=forms.Select(attrs={'placeholder': 'Auteurs', 'id':"pres_author2"}) )

class UploadForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ('fichier_pptx',)


class IntervenantForm(forms.Form):
    id = forms.CharField(label='', initial=-1,widget=forms.TextInput(attrs={'type': 'hidden', 'id':"inter_id"}) )
    nom = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'Nom intervenant', 'id':"inter_name"}) )
    prenom = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder': 'Prenom', 'id':"inter_surname"}) )
    logo = forms.ImageField(label='',widget=forms.FileInput(attrs={'placeholder': 'Logo', 'id':"inter_logo"}) )
    
  

   