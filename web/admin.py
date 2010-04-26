from web.models import Event
from django.contrib import admin

class EventAdmin(admin.ModelAdmin):
	fields = ['name', 'html']

admin.site.register(Event, EventAdmin)

