from django.conf.urls.defaults import *
from django.conf import settings

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
    (r'^raids/(?P<raid_id>\d+)/$', 'web.views.raid_detail'),
    (r'^raids/public/(?P<public_hash>[0-9a-fA-F]+)/$', 'web.views.public_raid_detail'),
    (r'^register$', 'web.views.register'),
    (r'^contact$', 'web.views.contact'),
    (r'^login$', 'web.views.login'),
    (r'^logout$', 'web.views.logout'),
	(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/jorge/wow-tools/media/css'}),
		(r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/jorge/wow-tools/media/js'}),
		(r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/jorge/wow-tools/media/images'}),
	)

