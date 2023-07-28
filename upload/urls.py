from django.urls import path , re_path

from . import views

app_name='upload'
urlpatterns = [
    path('file', views.uploadfile, name='file'),
    path("absolute_path",views.absolute_path,name="absolute_path"),
]