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
import datetime
from pprint import pprint
import polyline
from polyline.codec import PolylineCodec
from django.core.serializers import serialize
import codecs
import sys

from chomper.models import *

# Kevin's Key
gmapper = googlemaps.Client(key='AIzaSyCUSkUaTU4DJhuheYoh3_x2y1BBD40N3yc')
# gmapper = googlemaps.Client(key='AIzaSyCUyRHrPjwl5F-hMit0-1lyZTyf6rKDMb8')


## Calculate all of the points needed in the route
def calcRoutePoints(ori,desi,modal):
    # # David's Key
    # gmapper = googlemaps.Client(key='AIzaSyBoORTHlDRQ2CRzQrssQfjT3r99xPJHjrE')

    results = {}
    t = datetime.time(8, 30, 0)

    d = datetime.date.today()

    dt = datetime.datetime.combine(d, t)


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
    # pprint(directions_result)
    durlist = dirleg['duration']
    durtext = durlist['text']
    lines = []
    for leg in directions_legs:
        steps = leg['steps']
        for step in steps:
            pline = step['polyline']['points']
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
        discardpoints = 7
        if (numpoints - (discardpoints * 2)) > 15:
            scalar = 2
    if mode == 'driving':
        segments = int(float(distance) / .5)
        scalar = int(float(numpoints) / float(segments))
    if mode == 'walking':
        segments = int(float(distance) / .25)
        scalar = int(float(numpoints) / float(segments))

    for point in intermediatepoints:
        if count > discardpoints and count % scalar == 1 and count < (numpoints - discardpoints):
            pointaddress = gmapper.reverse_geocode((point[0], point[1]))[0]['formatted_address'].encode('ascii', 'ignore')
            # pointaddress = pointaddress.strip(codecs.BOM_UTF8), 'utf-8'
            addresslist.append(pointaddress)
        count += 1

    return addresslist


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
        rp.name = rest['name']
        rp.rating = rest['rating']
        rp.isclosed = rest['closed']
        rp.address = rest['address']
        rp.save()
    restpointsjson = serialrestpoints()