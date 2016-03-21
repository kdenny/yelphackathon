from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from djgeojson.views import GeoJSONLayerView

from chomper import views

from chomper.models import IntermediatePoint, RouteLine, RestaurantPoint, UserPoint

router = DefaultRouter()
router.register(r'snippets', views.SnippetView)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^api/$', views.api_examples, name='api'),
    url(r'^data.geojson$', GeoJSONLayerView.as_view(model=RouteLine), name='data'),
    url(r'^datapoints.geojson$', GeoJSONLayerView.as_view(model=RestaurantPoint, properties=('name','rating','Color','popupContent')), name='datapoints'),
    url(r'^userpoints.geojson$', GeoJSONLayerView.as_view(model=UserPoint, properties=('name')), name='userpoints'),
    url(r'^popup/$', views.popup),
    url(r'^googlemaps/$', views.googlemaps, name='googlemaps'),
)
