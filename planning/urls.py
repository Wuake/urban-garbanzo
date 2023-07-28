from django.urls import path , re_path

from . import views

app_name='planning'
urlpatterns = [
    path('create', views.create, name='create'),
    path('show', views.show_plan, name='show'),
    path('planning', views.planning_plan, name='planning'),
    path('get-sessions/', views.get_sessions, name='get_sessions'),
    path('intervenant', views.show_intervenant, name='intervenant'),
    path('delete_intervenant/<int:intervenant_id>/', views.delete_intervenant, name='delete_intervenant'),
    path('pupitre', views.show_pupitre, name='pupitre'),
    path('upload', views.show_upload, name='upload'),
    path('upload_intervenant', views.intervenant_select, name='upload_intervenant'),
    path('open_pres', views.ouvrir_presentation, name='open_pres'),
    path('congres', views.addcongres, name='congres'),
    path("pajax/<int:pk>/<slug:date>", views.ajax_load_planning, name="planning-ajax"),
    path("sajax/<int:pk>/", views.ajax_add_session, name="session-ajax"),
    path("pajax/<int:pk>/", views.ajax_add_pres, name="pres-ajax"),
    path("dajax/<int:pk>/", views.ajax_del_pres, name="pres-del-ajax"),
    #ajout d'une salle
    path("salle-ajax/", views.addOneRoom, name="salle-ajax"),
    path("load-ajax/", views.ajax_load_rooms, name="load-ajax"),
    path("check_mark/", views.check_mark, name="check_mark"),
    path("on_laptop/", views.on_laptop, name="on_laptop"),
    path("fetching_files/", views.fetching_files, name="fetching_files"),
    path("couleur_bouton/", views.couleur_bouton, name="couleur_bouton"),
]
