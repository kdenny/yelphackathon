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
    """Calculates the list of all restaurant addresses

    Args:
        restaurants (list of dicts)
        cuisines (list): The list of all cuisines to search for.
        distance (int): The distance to search around each intermediate point

    Returns:
        restlist (list of dicts): The list of all restaurant results, containing dictionaries with the processed yelp results

    """
    addresslist = []
    for rest in restaurants:
        if 'address' in rest:
            addressstring = str(rest['address']) + ' ' + str(rest['city'])
            addresslist.append(addressstring)

    # pprint.pprint(addresslist)
    return addresslist

def getCuisines(ogcuisine):
    """Processes the input cuisine alias selected by the user, and selects the list of cuisines to query the Yelp API.

    Args:
        ogcuisine (str): The cuisine alias selected by the user

    Returns:
        cuisinecodes (list): The list of cuisines to be queried for the API

    """
    cuisinecodes = {}
    cuisinecodes['Fast Food'] = ['hotdogs', 'burgers', 'chickenshop']
    cuisinecodes['Burgers'] = ['burgers']
    cuisinecodes['Chicken'] = ['chickenshop']
    cuisinecodes['Fast Food'] = ['hotdogs']
    cuisinecodes['Cheesesteaks'] = ['cheesesteaks']
    cuisinecodes['Gastropubs'] = ['gastropubs']
    cuisinecodes['Diner / Breakfast'] = ['breakfast_brunch', 'diners']
    cuisinecodes['Breakfast'] = ['breakfast_brunch']
    cuisinecodes['Diner'] = ['diners']
    cuisinecodes['Casual'] = ['salad', 'sandwiches', 'soup']
    cuisinecodes['Salad'] = ['salad']
    cuisinecodes['Sandwiches'] = ['sandwiches']
    cuisinecodes['Soup'] = ['soup']
    cuisinecodes['Italian / Pizza'] = ['pizza', 'italian']
    cuisinecodes['Pizza'] = ['pizza']
    cuisinecodes['Italian'] = ['italian']
    cuisinecodes['African'] = ['african', 'ethiopian']
    cuisinecodes['American'] = ['newamerican', 'tradamerican']
    cuisinecodes['BBQ'] = ['bbq']
    cuisinecodes['French / Belgian'] = ['french', 'belgian']
    cuisinecodes['French'] = ['french']
    cuisinecodes['Belgian'] = ['belgian']
    cuisinecodes['Pub'] = ['british', 'irish']
    cuisinecodes['British'] = ['british']
    cuisinecodes['Irish'] = ['irish']
    cuisinecodes['Southern'] = ['cajun', 'soulfood', 'southern']
    cuisinecodes['Cajun'] = ['cajun']
    cuisinecodes['Caribbean'] = ['caribbean']
    cuisinecodes['Chinese'] = ['chinese']
    cuisinecodes['Latin American'] = ['cuban', 'latin', 'brazilian']
    cuisinecodes['Cuban'] = ['cuban']
    cuisinecodes['Latin'] = ['latin']
    cuisinecodes['Brazilian'] = ['brazilian']
    cuisinecodes['Mexican'] = ['mexican']
    cuisinecodes['Tex-Mex'] = ['tex-mex']
    cuisinecodes['Greek'] = ['greek']
    cuisinecodes['Indian'] = ['indpak']
    cuisinecodes['Japanese / Sushi'] = ['japanese', 'sushi']
    cuisinecodes['Japanese'] = ['japanese']
    cuisinecodes['Sushi'] = ['sushi']
    cuisinecodes['Mediterranean'] = ['mediterranean','mideastern','kosher']
    cuisinecodes['Middle Eastern'] = ['mideastern']
    cuisinecodes['Kosher'] = ['kosher']
    cuisinecodes['Seafood'] = ['seafood']
    cuisinecodes['Spanish / Tapas'] = ['tapasmallplates','spanish']
    cuisinecodes['Tapas / Small Plates'] = ['tapasmallplates']
    cuisinecodes['Spanish'] = ['spanish']
    cuisinecodes['Steakhouse'] = ['steak']
    cuisinecodes['Thai'] = ['thai']
    cuisinecodes['Vegetarian'] = ['vegetarian']
    cuisinecodes['Vietnamese'] = ['vietnamese']

    return cuisinecodes[ogcuisine]


def getRestaurantAddressDict(restaurants):
    """Creates a dictionary for identifying restaurants based on their address, to be used in distance matrix calculations.

    Args:
        restaurants (list of dicts) : processed data about the Yelp API

    Returns:
        addressdict (dict): The dictionary for identifying the restaurant at each point

    """
    addressdict = {}
    for rest in restaurants:
        if 'address' in rest:
            addressstring = str(rest['address']) + ' ' + str(rest['city'])
            addressdict[addressstring] = rest['name']

    return addressdict

def calcRestaurantList(addresses, cuisines, distance):
    """Calls the Yelp API to search around each intermediate route point the function to process the
    yelp results, and adds all new restaurants to a list.

    Args:
        addresses (list): The list of the addresses of all intermediate route points.
        cuisines (list): The list of all cuisines to search for.
        distance (int): The distance to search around each intermediate point

    Returns:
        restlist (list of dicts): The list of all restaurant results, containing dictionaries with the processed yelp results

    """
    restlist = []
    used = []
    print addresses
    cuisine = str(cuisines[0])
    if len(cuisines) > 1:
        cuisine = ",".join(cuisines)
    minrating = 5.0
    worst = ''
    ratings = []
    for point in addresses:
        yelpresults = search(cuisine,point,distance)['businesses']
        processedyelpresults = processResults(yelpresults)
        for result in processedyelpresults:
            if (result not in used):
                if len(restlist) < 40:
                    restlist.append(processedyelpresults[result])
                    used.append(result)
                    ratings.append(float(result['ratings']))
                    if float(processedyelpresults[result]['rating']) < minrating:
                        minrating = float(processedyelpresults[result]['rating'])
                        worst = result

                elif len(restlist) >= 40:
                    ratings.sort()
                    if float(processedyelpresults[result]['rating']) > minrating:
                        if worst in restlist:
                            restlist.remove(restlist.index(worst))
                            if len(restlist) < 45:
                                restlist.append(processedyelpresults[result])
                        else:
                            minrating = ratings[0]
                            for r in restlist:
                                if r['rating'] == minrating:
                                    worst = r['name']
                                    restlist.remove(r)
                                    minrating = r['rating']
                            if len(restlist) < 45:
                                restlist.append(processedyelpresults[result])

    print (len(restlist))
    pprint.pprint(restlist)
    print(used)

    return restlist

def calcRestaurantList2(latlngs, cuisines, distance):
    """Calls the Yelp API to search around each intermediate route point the function to process the
    yelp results, and adds all new restaurants to a list.

    Args:
        latlngs (list): The list of the lat / long pairs of all intermediate route points.
        cuisines (list): The list of all cuisines to search for.
        distance (int): The distance to search around each intermediate point

    Returns:
        restlist (list of dicts): The list of all restaurant results, containing dictionaries with the processed yelp results

    """
    restlist = []
    used = []
    cuisine = str(cuisines[0])
    if len(cuisines) > 1:
        cuisine = ",".join(cuisines)
    minrating = 5.0
    worst = ''
    ratings = []
    for point in latlngs:
        yelpresults = search2(cuisine,point,distance)['businesses']
        processedyelpresults = processResults(yelpresults)
        for result in processedyelpresults:
            if (result not in used):
                if len(restlist) < 40:
                    restlist.append(processedyelpresults[result])
                    used.append(result)
                    ratings.append(float(processedyelpresults[result]['rating']))
                    if float(processedyelpresults[result]['rating']) < minrating:
                        minrating = float(processedyelpresults[result]['rating'])
                        worst = result
                        # print ("The worst restaurant is {0}".format(worst))
                elif len(restlist) >= 40:
                    ratings.sort()
                    minrating = ratings[0]
                    if float(processedyelpresults[result]['rating']) > ratings[0] and ratings[0] < 3.5:
                        if worst in restlist:
                            ratings.remove(minrating)
                            restlist.remove(restlist.index(worst))
                            # print ("Removed {0}, which had a rating of {1}. It was in restlist".format(worst, minrating))
                            if len(restlist) <= 45:
                                restlist.append(processedyelpresults[result])
                                # print ("Added {0}, which had a rating of {1}".format(result, processedyelpresults[result]['rating']))
                        else:
                            minrating = float(ratings[0])
                            # print ("The minimum rating for a restaurant is {0}".format(minrating))
                            for r in restlist:
                                # print (r)
                                if float(r['rating']) == minrating:
                                    restlist.remove(r)
                                    # print ("Removed {0}, which had a rating of {1}. Matched on minrating".format(r, minrating))
                                    if minrating in ratings:
                                        ratings.remove(minrating)
                            if len(restlist) <= 45:
                                restlist.append(processedyelpresults[result])
                                # print ("Added {0}, which had a rating of {1}".format(result, processedyelpresults[result]['rating']))

    # pprint.pprint(restlist)
    # print(used)

    return restlist

def search(term, location, distance):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
        distance (int): The search distance to query from each route point.

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

def search2(term, location, distance):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
        distance (int): The search distance to query from each route point.

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
        'll': location.replace(' ', '+'),
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
    """Parses the results of the Yelp API query into a more logical and easy to use structure.

    Args:
        results (dict): The JSON response from the API.

    Returns:
        restaurantDict: The processed results into an easier to use format

    """
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