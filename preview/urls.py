"""preview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , re_path
from django.conf.urls import handler404, handler500, handler403, handler400
from django.conf.urls.static import static
from django.urls import include

from . import views
from planning.views import show_plan, planning_plan
from preview import settings

handler404 = 'preview.views.handler404'
handler500 = 'preview.views.handler500'

urlpatterns = [
    path('', views.home, name="home"),
    path('plan/', show_plan, name="show_plan"),
    path('planning/', planning_plan, name="planning_plan"),
    re_path(r'^planning/', include('planning.urls')),
    re_path(r'^upload/', include('upload.urls')),


# Admin Admin

    re_path(r'^admin/', admin.site.urls, name='admin'),
 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)