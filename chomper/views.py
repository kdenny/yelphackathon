# Django
from django.shortcuts import render, render_to_response
from django.contrib.auth import logout
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Django REST Framework
from rest_framework import viewsets, mixins

# Scripts
from scripts.yelp import calcRestaurantList, getRestaurantAddresses, getRestaurantAddressDict, getCuisines, calcRestaurantList2
from scripts.gmaps import calcRoutePoints, createAddressList, makeRestaurantPoints, calcRestaurantDistanceMatrix, addDistanceToRestaurants, createLatLngs

# Python
import oauth2 as oauth
import simplejson as json
import requests

# Models
from chomper.models import *
from chomper.serializers import SnippetSerializer
from chomper.forms import UserForm

cuisines = []
profile_track = None



def index(request):
    print "index: " + str(request.user)
    data = {}
    cuisine = request.POST.get('cuisine')
    friend = request.POST.get('user')

    dest = request.POST.get('destination')
    org = request.POST.get('origin')
    data['friend'] = friend


    context = {'hello': 'world'}
    return render_to_response('chomper/index.html', {'data': data, }, context_instance=RequestContext(request))
    # return render(request, 'chomper/index.html', context)


##################
#  API Examples  #
##################

def api_examples(request):
    context = {'title': 'API Examples Page'}
    return render(request, 'chomper/api_examples.html', context)


#################
# Google Maps API #
#################

def googlemaps(request):
    restaurants = {}
    datum = {}
    if request.method == 'POST':
        org = request.POST.get('origin')
        dest = request.POST.get('destination')
        mode = request.POST.get('mode')
        # if mode == '':
        #     mode = 'driving'
        ogcuisine = str(request.POST.get('cuisine'))
        cuisines = getCuisines(ogcuisine)

        routeresults = calcRoutePoints(org,dest,mode)
        points = routeresults['points']
        distance = routeresults['distance']
        duration = int(routeresults['durnum'])
        # addresses = createAddressList(org,dest,mode,distance,points)
        latlngs = createLatLngs(org,dest,mode,distance,points)
        # restaurants = calcRestaurantList(addresses,cuisines,distance)
        restaurants = calcRestaurantList2(latlngs,cuisines,distance)
        restaurantaddresses = getRestaurantAddresses(restaurants)
        restaurantaddressdict = getRestaurantAddressDict(restaurants)

        users = ['origin','destination']
        restaurantdistancematrix = calcRestaurantDistanceMatrix(restaurantaddresses,org,dest,mode,users,restaurantaddressdict)
        restaurants = addDistanceToRestaurants(restaurants,restaurantdistancematrix,restaurantaddressdict,duration)

        makeRestaurantPoints(restaurants)

        datum['numrest'] = len(restaurants)
        datum['cuisine'] = ogcuisine
        datum['origin'] = org
        datum['destination'] = dest
        datum['mode'] = mode
        datum['duration'] = routeresults['duration']
        print(datum)

    return render(request, 'chomper/googlemaps.html', { 'data': restaurants, 'datum': datum})



#########################
# Snippet RESTful Model #
#########################

class CRUDBaseView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    pass

class SnippetView(CRUDBaseView):
    serializer_class = SnippetSerializer
    queryset = Snippet.objects.all()


######################
# Registration Views #
######################

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
            return HttpResponseRedirect('/chomper/login/')
        else:
            print user_form.errors
    else:
        user_form = UserForm()


    return render(request,
            'chomper/register.html',
            {'user_form': user_form, 'registered': registered} )

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your Django Hackathon account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'chomper/login.html', {})

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/chomper/login/')


def popup(request):
    return render(request, 'popup.html')


