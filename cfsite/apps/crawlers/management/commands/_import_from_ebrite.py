import os
import urllib2
from urllib2 import URLError
import json
import json
import re
from datetime import datetime
from cfsite.apps.events.models import CONF, ART, MEET, FAM, CLASS, SPORT, FOOD, MUSIC
from cfsite.apps.crawlers.management.commands._errors import SourceRetrievalError

_EBRITE_KEY = "JO34L4OP3GCXGEC2XJ"
_EVENTS_PER_PAGE = 100

_EBRITE_TO_CF_CATEGORIES = {'conferences':CONF,
                           'conventions':CONF,
                           'entertainment':ART,
                           'fundraisers':MEET,
                           'meetings':MEET,
                           'other':MEET,
                           'performances':ART,
                           'reunions':MEET,
                           'sales':FAM,
                           'seminars':CLASS,
                           'social':MEET,
                           'sports':SPORT,
                           'tradeshows':CONF,
                           'travel':FAM,
                           'religion':FAM,
                           'fairs':FAM,
                           'food':FOOD,
                           'music':MUSIC,
                           'recreation':FAM}

def _price_str_to_float(price_str):
    return float(re.sub(u',',u'', price_str))

def get_and_parse_eventbrite_JSON(): # generator function
    """
    Get next page's worth of JSON from eventbrite and extract
    start time, name, category, (<--mandatory, if missing, disregard event)
    end time, price, address, description, website (<--optional, ok if missing)
    Return a list of dicts that contain this info, one dict per event
    """
    curr_page = 0
    num_shown_so_far = 0
    total_items = 0
    opener = urllib2.build_opener()
    while (curr_page == 0) or (num_shown_so_far < total_items):
        events_list = []
        curr_page +=1
        req = urllib2.Request(("https://www.eventbrite.com/json/event_search"
                               "?app_key=%s&city=Palo+Alto&region=CA&max=%d&page=%d"
                               % (_EBRITE_KEY, _EVENTS_PER_PAGE, curr_page)))
        try:
            f = opener.open(req)
        except URLError as e:
            raise SourceRetrievalError(e.reason)

        ebrite_events_dict = json.load(f)
        if u'error' in ebrite_events_dict:
            break

        try:
            total_items = ebrite_events_dict[u'events'][0][u'summary'][u'total_items']
            num_showing = ebrite_events_dict[u'events'][0][u'summary'][u'num_showing']
            num_shown_so_far += num_showing
        except KeyError:
            break

        for i in range(1,num_showing+1): # start from 1 because 0th is a summary dict
            ev_dict =  ebrite_events_dict[u'events'][i][u'event']
            try:
                name = ev_dict[u'title']
                categories = _get_cfsite_categories(ev_dict[u'category'].split(','))
                start_datetime = _convert_to_datetime(ev_dict[u'start_date'])
            except KeyError: # if any of 3 mandatory fields are missing, skip event
                continue
            cf_ev_dict = {'name':name, 'categories':categories, # 'location':loc,
                          'start_datetime':start_datetime}
            try:
                """
                Most KeyErrors should be avoided since we check if the key
                exists first, but we do make one assumption about what key
                *should* be there (if we have a list of tickets, the dicts inside
                should have key 'ticket')
                """
                _ebrite_extract_optional_fields(ev_dict, cf_ev_dict)
            except KeyError:
                print(sys.stderr, 'Error extracting optional info from event. Skipping.')
                traceback.print_exc(file=sys.stderr)
                continue

            events_list.append(cf_ev_dict)

        yield events_list

def _ebrite_extract_optional_fields(ev_dict, cf_ev_dict):
    # Going to do a lot of checks for keys, in case of malformed / missing data:
    if u'end_date' in ev_dict:
        cf_ev_dict['end_datetime'] = _convert_to_datetime(ev_dict[u'end_date'])

    if u'tickets' in ev_dict:
        priced_tickets = _discard_tickets_without_price(ev_dict[u'tickets'])
        if priced_tickets:
            min_price = _price_str_to_float(
                priced_tickets[0][u'ticket'][u'price'])
            for ticket_info in priced_tickets:
                ticket_price = _price_str_to_float(
                    ticket_info[u'ticket'][u'price'])
                min_price = ticket_price if ticket_price < min_price else min_price
            cf_ev_dict['price'] = min_price

    if u'description' in ev_dict:
        cf_ev_dict['description'] = ev_dict[u'description']

    if u'url' in ev_dict:
        cf_ev_dict['url'] = ev_dict[u'url']

    if u'venue' in ev_dict and u'address' in ev_dict[u'venue']:
        cf_ev_dict['address'] = ev_dict[u'venue'][u'address']

def _discard_tickets_without_price(tickets):
    """
    Takes in a list of tickets {u'ticket': {u'description': u'', ...}}
    Returns a list of tickets with ones without prices removed
    """
    return filter(lambda ticket: u'price' in ticket[u'ticket'], tickets)

def _get_cfsite_categories(ebrite_categories):
    """
    Takes a list of eventbrite categories and
    returns corresponding crazyfish categories.
    """
    cf_categories = set()
    for cat in ebrite_categories:
        cf_categories.add(_EBRITE_TO_CF_CATEGORIES[cat])
    return list(cf_categories)


def _convert_to_datetime(ebrite_date_str):
    """
    Takes eventbrite start or end date and time
    Returns a datetime object.
    """
    dt_list = re.findall(r'[0-9]+', ebrite_date_str)
    assert(len(dt_list)==6) # must be six elements, 3 for date, 3 for time
    dt_int_list = [int(num_str) for num_str in dt_list]
    return datetime(dt_int_list[0], dt_int_list[1], dt_int_list[2],
                             dt_int_list[3], dt_int_list[4], dt_int_list[5])