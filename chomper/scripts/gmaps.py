# pylint: disable=invalid-name

'''
Gmaps.py contains methods for
authenticating the user and
retrieving data from Google's Directions, Geocoding and Reverse Geocoding APIs.
'''

import simplejson as json
import oauth2
import requests
import googlemaps
from pprint import pprint
import polyline
from polyline.codec import PolylineCodec
from django.core.serializers import serialize
import codecs
import sys

from chomper.models import *

# Kevin's Key
# gmapper = googlemaps.Client(key='AIzaSyCUSkUaTU4DJhuheYoh3_x2y1BBD40N3yc')
gmapper = googlemaps.Client(key='AIzaSyCUyRHrPjwl5F-hMit0-1lyZTyf6rKDMb8')



## Calculate all of the points needed in the route
def calcRoutePoints(ori,desi,modal):
    # # David's Key
    # gmapper = googlemaps.Client(key='AIzaSyBoORTHlDRQ2CRzQrssQfjT3r99xPJHjrE')

    print("Start calculating route points")
    print("")

    results = {}


    travelTimes = {}

    destination = desi

    origin = ori

    routepoints = {}
    allroutepoints = {}
    routepolylines = {}


    points = []
    polyline = []

    directions_result = gmapper.directions(origin,destination,mode=modal)
    directions_legs = (directions_result[0]['legs'])
    dirleg = directions_legs[0]
    distlist = dirleg['distance']
    disttext = distlist['text']
    distnum = disttext.replace(" mi","")
    pprint(directions_result)
    durlist = dirleg['duration']
    durtext = durlist['text']
    lines = []
    for leg in directions_legs:
        steps = leg['steps']
        for step in steps:
            pline = step['polyline']['points']
            tmode = step['travel_mode']
            polyline.append(pline)
            pts = PolylineCodec().decode(pline)
            lines.append(pts)
            for pt in pts:
                if pt not in points:
                    points.append(pt)


    routepoints = points
    routepolylines = lines

    makePoints(points)
    makeLines(points)
    # polylineshp = 'C:/CommutrTest/Shapefiles/RoutePolylines2.shp'
    # convert_to_shapefile(routepoints,polylineshp)

    results['points'] = points
    results['distance'] = distnum
    results['duration'] = durtext

    return results

def createAddressList(origin,destination,mode,distance,intermediatepoints):
    addresslist = [origin, destination]
    numpoints = len(intermediatepoints)
    scalar = 10
    discardpoints = 3
    segments = 10
    count = 1

    if mode == 'transit':
        scalar = 1
        discardpoints = 5
        if (numpoints - (discardpoints * 2)) > 25:
            scalar = 2
    if mode == 'driving':
        segments = int(float(distance) / .5)
        scalar = int(float(numpoints) / float(segments))
    if mode == 'walking':
        segments = int(float(distance) / .25)
        scalar = int(float(numpoints) / float(segments))

    for point in intermediatepoints:
        if count > discardpoints and (count % scalar == 1 or scalar == 1) and count < (numpoints - discardpoints) and ((count > 1) and (intermediatepoints[count] != intermediatepoints[count-1])):
            pointaddress = gmapper.reverse_geocode((point[0], point[1]))[0]['formatted_address'].encode('ascii', 'ignore')
            # pointaddress = pointaddress.strip(codecs.BOM_UTF8), 'utf-8'
            if pointaddress not in addresslist:
                addresslist.append(pointaddress)
        count += 1

    return addresslist


def calcRestaurantDistanceMatrix(restaurants,origin,destination,modal,users,addressdict):
    userpoints = [origin, destination]

    gmappr = googlemaps.Client(key='AIzaSyB17F8Q89ZuNlPN3fAXinQUDK83Bufmmto')
    rmatrix = gmappr.distance_matrix(restaurants, userpoints, mode=modal)['rows']

    allrestresults = {}
    restcount = 0
    for rest in rmatrix:
        restresults = {}
        aresult = rest['elements']
        count = 0
        for result in aresult:
            if 'duration' in result:
                durtext = str(result['duration']['text'])
                duration = durtext.replace(" mins","")
                duration = duration.replace(" min","")
                x = 'hours'
                nduration = ''

                if x in duration:
                    xind = duration.index(x)
                    hoursub = duration[:xind]
                    time = int(hoursub) * 60
                    minsub = duration[(xind + 6):]
                    nduration = int(time) + int(minsub)

                y = 'hour'

                if y in duration and x not in duration:
                    xind = duration.index(y)
                    hoursub = duration[:xind]
                    time = int(hoursub) * 60
                    minsub = duration[(xind + 5):]
                    nduration = int(time) + int(minsub)

                if y not in duration and x not in duration:
                    nduration = int(duration)

                restresults[users[count]] = nduration
            elif 'duration' not in result:
                restresults[users[count]] = 0

            count += 1

        allrestresults[addressdict[restaurants[restcount]]] = restresults
        restcount += 1

    pprint (allrestresults)

    return allrestresults

def addDistanceToRestaurants(restaurants, distancematrix, addressdict):
    newrests = []
    for rest in restaurants:
        if rest['name'] in distancematrix:
            rest['distances'] = distancematrix[rest['name']]
            newrests.append(rest)
        else:
            addressstring = str(rest['address']) + ' ' + str(rest['city'])
            otherrest = addressdict[addressstring]
            rest['distances'] = distancematrix[otherrest]
            newrests.append(rest)

    return newrests

def makePoints(points):
    count = 1
    for point in points:
        ip = IntermediatePoint()
        ip.geom = {'type': 'Point', 'coordinates': [point[1], point[0]]}
        ip.name = '{0}'.format(count)
        ip.save()
        count = count + 1

def makeLines(points):
    count = 1
    RouteLine.objects.all().delete()
    li = RouteLine()
    coords = []
    for point in points:
        if len(point) <= 2:
            a = [point[1], point[0]]
            coords.append(a)

    li.geom = {'type': 'LineString', 'coordinates': coords}
    li.save()
    linesgeojson = seriallines()


def seriallines():
    return serialize('geojson', RouteLine.objects.all(),
              geometry_field='geom')

def serialrestpoints():
    return serialize('geojson', RestaurantPoint.objects.all(),
              geometry_field='geom')


def makeRestaurantPoints(restaurants):
    RestaurantPoint.objects.all().delete()
    for rest in restaurants:
        rp = RestaurantPoint()
        rp.geom = {'type': 'Point', 'coordinates': [rest['coords'][1], rest['coords'][0]]}
        rp.name = rest['name'].encode('ascii', 'ignore')
        rp.rating = rest['rating'].encode('ascii', 'ignore')
        rp.isclosed = rest['closed']
        rp.address = rest['address']
        rp.save()
    restpointsjson = serialrestpoints()