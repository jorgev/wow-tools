from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^web/', include('web.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
	(r'^$', 'web.views.index'),
	(r'^upload$', 'web.views.upload'),
    (r'^raids$', 'web.views.raids'),
    (r'^raids/(?P<raid_id>\d+)/$', 'web.views.raids'),
	(r'^admin/', include(admin.site.urls)),
)
