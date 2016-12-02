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
            "maxStops": 0,
            }
        ],
        "solutions": 3,
        }
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    results = response.json()
    logger.info('%r', request)

    # logger.info('%r to %r', flight_set[0], flight_set[1])
    flight_path = results['trips']
    # for num in xrange(0,1):
    #     logger.info('%r', flight_path['tripOption'][num]['saleTotal'])
    #     logger.info('%r', flight_path['data']['city'][0]['name'])
    #     logger.info('%r', flight_path['data']['city'][1]['name'])
    #     logger.info('%r', flight_path['data']['carrier'][0]['name'])


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
