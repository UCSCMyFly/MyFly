# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

import requests
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
            pairs = make_pairs(unode.sources, unode.destinations)
            travel_date = date.today() + timedelta(days=30)
            for pair in pairs:
                # logger.info('%r', pair[0])
                get_flights(travel_date, pair)

    return dict(message='index',
                some='banana')

def get_flights(date, pair):

    url = 'https://www.googleapis.com/qpxExpress/v1/trips/search'
    request = {
        "request": {
        "maxPrice": "USD 1500",
        "passengers": {
          "adultCount": 1,
          "childCount": 0,
          "infantInLapCount": 0,
          "infantInSeatCount": 0,
          "kind": "qpxexpress#passengerCounts",
          "seniorCount": 0
        },
        "refundable": False,
        "saleCountry": "US",
        "slice": [
          {
            "alliance": "",
            "date": date,
            "destination": pair[1],
            "kind": "qpxexpress#sliceInput",
            "maxConnectionDuration": 150,
            "maxStops": 2,
            "origin": pair[0],
            "permittedCarrier": [
              "AA",
              "AS",
              "RC",
              "MX",
              "NW",
              "UA",
              "NH",
              "CA",
              "BA",
              "OS",
              "FB",
              "CI"
            ],
            "permittedDepartureTime": {
              "earliestTime": "00:00",
              "kind": "qpxexpress#timeOfDayRange",
              "latestTime": "23:59"
            },
            "preferredCabin": "COACH",
            "prohibitedCarrier": []
            }
        ],
        "solutions": 10,
        "ticketingCountry": "US"
        }
    }
    r = requests.get(url, data=request)
    logger.info('%r', r)


def make_pairs(sources, destinations):
    pairs = []
    for source in sources:
        for dest in destinations:
            if source != dest:
                pairs.append([source, dest])
    return pairs

@auth.requires_login()
def manage():
    form1 = FORM(INPUT(_name='name', requires=IS_IN_DB(db, 'airports.airport_name', '%(airport_name)s')),
               INPUT(_type='submit'))
    form2 = FORM(INPUT(_name='name', requires=IS_IN_DB(db, 'airports.airport_name', '%(airport_name)s')),
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
        destinations = unode.destinations
        if request.vars.name not in destinations:
            destinations.append(request.vars.name)
            db(db.user_nodes.user_email==auth.user.email).update(destinations=destinations)
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
