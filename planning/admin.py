from django.contrib import admin

from .models import Congress
from .models import Day
from .models import Room
from .models import Session
from .models import Presentation, Intervenant, InterPresent


# Register your models here.


class CongressAdmin(admin.ModelAdmin):
    ist_display = ( 'name', 'number')
    readonly_fields = ('id',)

    
class SessionAdmin(admin.ModelAdmin):
    list_display = ( 'room', 'date', 'title', 'order')
    search_fields = ('title',)
    list_filter = ('date',)
    ordering = ('-date',)
    
admin.site.register(Session, SessionAdmin)

admin.site.register([Day, Room, Presentation, Congress, Intervenant, InterPresent])