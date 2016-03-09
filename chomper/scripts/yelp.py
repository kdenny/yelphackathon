# pylint: disable=invalid-name

'''
Yelp.py contains methods for
authenticating the user and
retrieving data from Yelp's API.
'''

import simplejson as json
import oauth2
import requests
import argparse
import pprint
import sys
import urllib
import urllib2
import oauth2

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = 'EXMisJNWez_PuR5pr06hyQ'
CONSUMER_SECRET = 'VCK-4cDjtQ9Ra4HC5ltClNiJFXs'
TOKEN = 'AWYVs7Vim7mwYyT1BLJA2xhNTs_vXLYS'
TOKEN_SECRET = 'Rv4GrlYxYGhxUs14s0VBfk7JLJY'

API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'pizza'
DEFAULT_LOCATION = 'Washington, DC'
SEARCH_LIMIT = 3
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'


def getRestaurantAddresses(restaurants):
    addresslist = []
    for rest in restaurants:
        if 'address' in rest:
            addressstring = str(rest['address']) + ' ' + str(rest['city'])
            addresslist.append(addressstring)

    pprint.pprint(addresslist)
    return addresslist

def getCuisines(ogcuisine):
    cuisinecodes = {}
    cuisinecodes['Fast Food'] = ['hotdogs', 'burgers', 'chickenshop']
    cuisinecodes['Diner / Breakfast'] = ['breakfast_brunch', 'diners']
    cuisinecodes['Casual'] = ['salad', 'sandwiches', 'soup']
    cuisinecodes['Italian / Pizza'] = ['pizza', 'italian']
    cuisinecodes['African'] = ['african', 'ethiopian']
    cuisinecodes['American'] = ['newamerican', 'tradamerican', 'gastropubs', 'burgers', 'cheesesteaks']
    cuisinecodes['BBQ'] = ['bbq']
    cuisinecodes['French / Belgian'] = ['french', 'belgian']
    cuisinecodes['Pub'] = ['british', 'irish']
    cuisinecodes['Southern'] = ['cajun', 'soulfood', 'southern']
    cuisinecodes['Caribbean'] = ['caribbean']
    cuisinecodes['Chinese'] = ['chinese']
    cuisinecodes['Latin American'] = ['cuban', 'latin', 'brazilian']
    cuisinecodes['Mexican'] = ['mexican', 'tex-mex']
    cuisinecodes['Greek'] = ['greek']
    cuisinecodes['Indian'] = ['indpak']
    cuisinecodes['Japanese / Sushi'] = ['japanese', 'sushi']
    cuisinecodes['Mediterranean'] = ['mediterranean','mideastern','kosher']
    cuisinecodes['Seafood'] = ['seafood']
    cuisinecodes['Spanish / Tapas'] = ['tapasmallplates','spanish']
    cuisinecodes['Steakhouse'] = ['steak']
    cuisinecodes['Thai'] = ['thai']
    cuisinecodes['Vegetarian'] = ['vegetarian']
    cuisinecodes['Vietnamese'] = ['vietnamese']

    return cuisinecodes[ogcuisine]


def getRestaurantAddressDict(restaurants):
    addressdict = {}
    for rest in restaurants:
        if 'address' in rest:
            addressstring = str(rest['address']) + ' ' + str(rest['city'])
            addressdict[addressstring] = rest['name']

    return addressdict

def calcRestaurantList(addresses, cuisines, distance):
    restlist = []
    used = []
    print addresses

    for point in addresses:
        for cuisine in cuisines:
            yelpresults = search(cuisine,point,distance)['businesses']
            processedyelpresults = processResults(yelpresults)
            for result in processedyelpresults:
                if (result not in used):
                    restlist.append(processedyelpresults[result])
                    used.append(result)

    pprint.pprint(restlist)
    print(used)

    return restlist


def search(term, location, distance):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """

    print location

    scalar = 1
    if distance > 5:
        scalar = int(float(distance) / 5.0)

    url_params = {
        'category_filter': term.replace(' ', '+'),
        'radius_filter': 1000,
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)

def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'https://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(
        method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(
        oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()

    print u'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def processResults(results):
    restaurantDict = {}
    for result in results:
        rdict = {}
        name = result['name']
        location = result['location']
        rdict['name'] = name
        rdict['url'] = result['mobile_url']
        rdict['cuisine'] = result['categories']
        rdict['closed'] = result['is_closed']
        rdict['address'] = location['display_address'][0]
        if 'neighborhoods' in location:
            rdict['neighborhood'] = location['neighborhoods'][0]
        else:
            rdict['neighborhood'] = 'N/A'
        if 'display_phone' in result:
            rdict['phone'] = result['display_phone']
        rdict['city'] = str(location['city']) + ", " + str(location['state_code'])
        rdict['rating'] = str(result['rating'])
        if ('coordinate' in result['location']):
            rdict['coords'] = [result['location']['coordinate']['latitude'], result['location']['coordinate']['longitude']]
            if rdict['city'] != rdict['address']:
                restaurantDict[name] = rdict

    return restaurantDict