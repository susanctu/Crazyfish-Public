from django.conf.urls import patterns, include, url
from django.contrib import admin
from cfsite.apps.events.views import home, search


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cfsite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', home, name='home'),
    url(r'^search/$', search),
    url(r'^admin/', include(admin.site.urls)),
)
