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
from scripts.twitter import TwitterOauthClient
from scripts.nytimes import *
from scripts.linkedin import LinkedinOauthClient
from scripts.yelp import calcRestaurantList, getRestaurantAddresses, getRestaurantAddressDict, getCuisines
from scripts.facebook import *
from scripts.gmaps import calcRoutePoints, createAddressList, makeRestaurantPoints, calcRestaurantDistanceMatrix

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
getTwitter = TwitterOauthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET, settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)
getLinkedIn = LinkedinOauthClient(settings.LINKEDIN_CLIENT_ID, settings.LINKEDIN_CLIENT_SECRET)
getFacebook = FacebookOauthClient(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)



def index(request):
    print "index: " + str(request.user)
    data = {}
    cuisine = request.POST.get('cuisine')
    date = request.POST.get('date')
    friend = request.POST.get('user')

    dest = request.POST.get('destination')
    org = request.POST.get('origin')
    data['date'] = date
    data['friend'] = friend

    if not request.user.is_active:
        if request.GET.items():
            if profile_track == 'twitter':
                oauth_verifier = request.GET['oauth_verifier']
                getTwitter.get_access_token_url(oauth_verifier)

                try:
                    user = User.objects.get(username = getTwitter.username + '_twitter')#(username=getTwitter.username)
                except User.DoesNotExist:
                    username = getTwitter.username + '_twitter'
                    new_user = User.objects.create_user(username, username+'@madewithtwitter.com', 'password')
                    new_user.save()
                    profile = TwitterProfile(user = new_user,oauth_token = getTwitter.oauth_token, oauth_token_secret= getTwitter.oauth_token_secret, twitter_user=getTwitter.username)
                    profile.save()
                user = authenticate(username=getTwitter.username+'_twitter', password='password')
                login(request, user)


            elif profile_track == 'linkedin':
                code = request.GET['code']
                getLinkedIn.get_access_token(code)
                getLinkedIn.getUserInfo()

                try:
                    user = User.objects.get(username=getLinkedIn.user_id+'_linkedin')
                except User.DoesNotExist:
                    username = getLinkedIn.user_id+'_linkedin'
                    new_user = User.objects.create_user(username, username+'@madwithlinkedin.com', 'password')
                    new_user.save()
                    try:
                        profile =LinkedinProfile.objects.get(user = new_user.id)
                        profile.access_token = LinkedinProfile.access_token
                    except LinkedinProfile.DoesNotExist:
                        profile = LinkedinProfile(user=new_user, access_token=getLinkedIn.access_token, linkedin_user=getLinkedIn.user_id)
                    profile.save()
                user = authenticate(username=getLinkedIn.user_id+'_linkedin', password='password')
                login(request, user)

            elif profile_track == 'facebook':
                code = request.GET['code']
                getFacebook.get_access_token(code)
                userInfo = getFacebook.get_user_info()
                username = userInfo['first_name'] + userInfo['last_name']

                try:
                    user = User.objects.get(username=username+'_facebook')
                except User.DoesNotExist:
                    new_user = User.objects.create_user(username+'_facebook', username+'@madewithfacbook', 'password')
                    new_user.save()

                    try:
                        profile = FacebookProfile.objects.get(user=new_user.id)
                        profile.access_token = getFacebook.access_token
                    except:
                        profile = FacebookProfile()
                        profile.user = new_user
                        profile.fb_user_id = userInfo['id']
                        profile.profile_url = userInfo['link']
                        profile.access_token = getFacebook.access_token
                    profile.save()
                user = authenticate(username=username+'_facebook', password='password')
                login(request, user)



    else:
        if request.GET.items():
            user = User.objects.get(username = request.user.username)
            if profile_track == 'twitter':
                oauth_verifier = request.GET['oauth_verifier']
                getTwitter.get_access_token_url(oauth_verifier)

                try:
                    twitterUser = TwitterProfile.objects.get(user = user.id)
                except TwitterProfile.DoesNotExist:
                    profile = TwitterProfile(user = user, oauth_token = getTwitter.oauth_token, oauth_token_secret= getTwitter.oauth_token_secret, twitter_user=getTwitter.username)
                    profile.save()

            elif profile_track == 'linkedin':
                code = request.GET['code']
                getLinkedIn.get_access_token(code)
                getLinkedIn.getUserInfo()

                try:
                    linkedinUser = LinkedinProfile.objects.get(user=user.id)
                except LinkedinProfile.DoesNotExist:
                    profile = LinkedinProfile(user = user, access_token = getLinkedIn.access_token, linkedin_user=getLinkedIn.user_id)
                    profile.save()


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
#  FACEBOOK API #
#################

def facebook(request):
    '''
    This is an example of getting basic user info and display it
    '''
    userInfo = getFacebook.get_user_info()
    return render(request, 'chomper/facebookAPIExample.html', { 'userInfo' : userInfo})





#################
# Google Maps API #
#################

def googlemaps(request):
    restaurants = {}
    datum = {}
    if request.method == 'POST':
        org = request.POST.get('origin')
        dest = request.POST.get('destination')
        mode = 'driving'
        mode = request.POST.get('mode')
        if mode == 'None':
            mode = 'driving'
        ogcuisine = str(request.POST.get('cuisine'))
        # cuisine = getCuisines(ogcuisine)
        cuisines = getCuisines(ogcuisine)

        routeresults = calcRoutePoints(org,dest,mode)
        points = routeresults['points']
        distance = routeresults['distance']
        addresses = createAddressList(org,dest,mode,distance,points)
        restaurants = calcRestaurantList(addresses,cuisines)
        restaurantaddresses = getRestaurantAddresses(restaurants)
        restaurantaddressdict = getRestaurantAddressDict(restaurants)

        users = ['me','Barry O.']
        restaurantdistancematrix = calcRestaurantDistanceMatrix(restaurantaddresses,org,dest,mode,users,restaurantaddressdict)
        # restaurants = addDistanceToRestaurants(restaurants,restaurantdistancematrix)

        makeRestaurantPoints(restaurants)

        datum['numrest'] = len(restaurants)
        datum['cuisine'] = ogcuisine
        datum['origin'] = org
        datum['destination'] = dest
        datum['mode'] = mode
        datum['duration'] = routeresults['duration']
        print(datum)

    return render(request, 'chomper/googlemaps.html', { 'data': restaurants, 'datum': datum})



#################
#  NYTIMES API  #
#################

def nytimespop(request):
    '''Returns JSON response about the most viewed articles for the last 24 hours.'''
    popdata = fetcharticle(settings.POPAPIKEY, 'http://api.nytimes.com/svc/mostpopular/v2/mostviewed/all-sections/1.json?')
    return JSONResponse({'data': popdata})

def nytimestop(request):
    '''Returns JSON response about the articles located in the homepage'''
    topdata = fetcharticle(settings.TOPAPIKEY, 'http://api.nytimes.com/svc/topstories/v1/home.json?')
    return JSONResponse({'data': topdata})

def nytimesarticles(request):
    everyData = {}
    popdata = fetcharticle(settings.POPAPIKEY, 'http://api.nytimes.com/svc/mostpopular/v2/mostviewed/all-sections/1.json?')
    topdata = topdata = fetcharticle(settings.TOPAPIKEY, 'http://api.nytimes.com/svc/topstories/v1/home.json?')
    everyData['top'] = topdata
    everyData['pop'] = popdata
    return render(request, 'chomper/nytimes.html', { 'everyData': everyData })


####################
#   TWITTER API    #
####################

def twitter(request):
    if getTwitter.is_authorized:
        value = getTwitter.get_trends_available(settings.YAHOO_CONSUMER_KEY)
    else:
        global profile_track
        profile_track = 'twitter'
        twitter_url = getTwitter.get_authorize_url()
        return HttpResponseRedirect(twitter_url)

    context ={'title': 'twitter', 'value': value}
    return render(request, 'chomper/twitter.html', context)

def twitterTweets(request):
    print getTwitter.is_authorized
    if getTwitter.is_authorized:
        if request.method == 'GET':
            if request.GET.items():
                tweets = request.GET.get('tweets')
                content, jsonlist = getTwitter.get_tweets(tweets)
            else:
                content, jsonlist = '', ''
    else:
        global profile_track
        profile_track = 'twitter'
        twitter_url = getTwitter.get_authorize_url()
        return HttpResponseRedirect(twitter_url)

    context ={'title': 'twitter tweet', 'content': content, 'data': jsonlist}
    return render(request, 'chomper/twitter_tweet.html', context)


##################
#  LINKEDIN  API #
##################

def linkedin(request):
    if getLinkedIn.is_authorized:
        content = getLinkedIn.getUserInfo()
    else:
        global profile_track
        profile_track = 'linkedin'
        linkedin_url = getLinkedIn.get_authorize_url()
        return HttpResponseRedirect(linkedin_url)

    context = {'title': 'linkedin example', 'content': content}
    return render(request, 'chomper/linkedin.html', context)


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



def twitter_login(request):
    global profile_track
    profile_track = 'twitter'
    twitter_url = getTwitter.get_authorize_url()
    return HttpResponseRedirect(twitter_url)

def linkedin_login(request):
    global profile_track
    profile_track = 'linkedin'
    linkedin_url = getLinkedIn.get_authorize_url()
    return HttpResponseRedirect(linkedin_url)

def facebook_login(request):
    global profile_track
    profile_track = 'facebook'
    facebook_url = getFacebook.get_authorize_url()
    return HttpResponseRedirect(facebook_url)


