from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from djgeojson.views import GeoJSONLayerView

from chomper import views

from chomper.models import IntermediatePoint, RouteLine, RestaurantPoint

router = DefaultRouter()
router.register(r'snippets', views.SnippetView)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^api/$', views.api_examples, name='api'),
    url(r'^data.geojson$', GeoJSONLayerView.as_view(model=RouteLine), name='data'),
    url(r'^datapoints.geojson$', GeoJSONLayerView.as_view(model=RestaurantPoint, properties=('name','rating','popupContent')), name='datapoints'),
    url(r'^googlemaps/$', views.googlemaps, name='googlemaps'),
    url(r'^linkedin/$', views.linkedin, name='linkedin'),
    url(r'^twitter/$', views.twitter, name='twitter'),
    url(r'^twitterTweets/$', views.twitterTweets, name='twitterTweets'),
    url(r'^twitter_login/$', views.twitter_login, name='twitter_login'),
    url(r'^linkedin_login/$', views.linkedin_login, name='linkedin_login'),
    url(r'^facebook_login/$', views.facebook_login, name='facebook_login'),
    url(r'^facebook/$', views.facebook, name='facebook'),
    url(r'^nytimespop/$', views.nytimespop, name='nytimespop'),
    url(r'^nytimestop/$', views.nytimestop, name='nytimestop'),
    url(r'^nytimesarticles/$', views.nytimesarticles, name='nytimesarticles'),
)
