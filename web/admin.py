from web.models import Event
from django.contrib import admin

class EventAdmin(admin.ModelAdmin):
	fields = ['name', 'user', 'html']
	list_display = ('name', 'user', 'created')
	list_filter = ['user']
	search_fields = ['user']
	date_hierarchy = 'created'

admin.site.register(Event, EventAdmin)
