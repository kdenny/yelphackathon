from django.conf.urls import patterns, include, url
from django.contrib import admin
from chomper import views

urlpatterns = patterns('',
    # url(r'^$', views.index, name='index'),
    url(r'^$', views.googlemaps, name='index'),
    url(r'^chomper/', include('chomper.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^openid/(.*)', SessionConsumer()),
)