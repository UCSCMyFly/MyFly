# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


#import request
import requests, json
from datetime import date, datetime, timedelta

import logging
logger = logging.getLogger("web2py.app.myfly")
logger.setLevel(logging.DEBUG)

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """


    if auth.user:
        unode = db.user_nodes(user_email = auth.user.email)
        if unode != None:
            sets = make_flight_sets(unode)
            travel_date = (date.today() + timedelta(days=30)).isoformat()
            for flight_set in sets:
                logger.info('%r', 'USD ' + str(flight_set[2]))
                get_flights(travel_date, flight_set)

    return dict(message='',
                some='')

def get_flights(date, flight_set):
    api_key = "AIzaSyAYyM6_C60GEHV5MnCcTCVhPpr9LTlwPE0"
    url = 'https://www.googleapis.com/qpxExpress/v1/trips/search?key=' + api_key
    headers = {'content-type': 'application/json'}
    data = {
        "request": {
        "maxPrice": 'USD' + str(flight_set[2]),
        "passengers": {
          "adultCount": 1,
        },
        "slice": [
          {
            "date": date,
            "destination": flight_set[1],
            "origin": flight_set[0],
            "maxStops": 1,
            }
        ],
        "solutions": 3,
        }
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    results = response.json()
    ##logger.info('%r', results)

    from_code = flight_set[0]
    dest_code = flight_set[1]
    travel_date = date
    source_name = ''
    source_airline = ''
    destination_name = ''
    price_of_flight = ''
    time_of_flight = ''

    list_of_flights = []

    # Get the airline first
    for city in results['trips']['data']['airport']:
        if city['code'] == from_code:
            source_name = city['name']
        if city['code'] == dest_code:
            destination_name = city['name']

    for solution in results['trips']['tripOption']:
        price_of_flight = solution['saleTotal']
        time_of_flight = solution['slice'][0]['segment'][0]['leg'][0]['departureTime']
        airline_code = solution['slice'][0]['segment'][0]['flight']['carrier']
        for airline in results['trips']['data']['carrier']:
            if airline_code == airline['code']:
                source_airline = airline['name']
        ##logger.info('\nFROM_CODE: %r\nDEST_CODE: %r\nTRAVEL_DATE: %r\nSOURCE_NAME: %r\nDEST_NAME: %r\nPRICE: %r\nTIME: %r\nSOURCE_AIRLINE: %r', from_code, dest_code, travel_date,source_name, destination_name, price_of_flight, time_of_flight, source_airline)
        flight_into_list = {'from':from_code,'to':dest_code,'date':travel_date,'source_name': source_name,'dest_name': destination_name,'price': price_of_flight,'time': time_of_flight,'airline': source_airline}
        list_of_flights.append(flight_into_list)
    logger.info('%r', list_of_flights)
    return list_of_flights

def make_flight_sets(unode):
    pairs = []
    sources = unode.sources
    destinations = unode.destinations
    prices = unode.dest_prices
    for source in sources:
        for i  in xrange(0, len(destinations)):
        # for dest, price in destinations, prices:
            if source != destinations[i]:
                pairs.append([source, destinations[i], prices[i]])
    return pairs

@auth.requires_login()
def manage():
    form1 = FORM(INPUT(_name='name', requires=IS_IN_DB(db, 'airports.airport_name', '%(airport_name)s')),
                 INPUT(_type='submit'))
    form2 = FORM(INPUT(_name='name', requires=IS_IN_DB(db, 'airports.airport_name', '%(airport_name)s')),
                 INPUT(_name='price', requires=IS_INT_IN_RANGE(1, 100000, error_message='price cant be negative')),
                 INPUT(_type='submit'))
    unode = db.user_nodes(user_email = auth.user.email)
    if unode is None:
        node_id = db.user_nodes.insert(user_email=auth.user.email)
        unode = db.user_nodes(id=node_id)

    if form1.process(formname='form_one').accepted:
        sources = unode.sources
        if request.vars.name not in sources:
            sources.append(request.vars.name)
            db(db.user_nodes.user_email==auth.user.email).update(sources=sources)
            response.flash = 'form one accepted ' + request.vars.name

    if form2.process(formname='form_two').accepted:
        logger.info('%r', unode)
        destinations = unode.destinations
        prices = unode.dest_prices
        if request.vars.name not in destinations:
            destinations.append(request.vars.name)
            prices.append(int(request.vars.price))
            db(db.user_nodes.user_email==auth.user.email).update(destinations=destinations, dest_prices=prices)
            response.flash = 'form two accepted'

    return dict(form1=form1, form2=form2)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
