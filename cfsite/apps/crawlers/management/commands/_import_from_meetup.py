import os
import urllib2
from urllib2 import URLError
import json
from datetime import datetime
from cfsite.apps.events.models import MEET
from cfsite.apps.crawlers.management.commands._errors import SourceRetrievalError

_MEETUP_KEY = "6865607a3c4b4d7d52946910646fc"
_EVENTS_PER_PAGE = 100

def get_and_parse_meetup_JSON(): # generator function
    """
    Get next page's worth of JSON from meetup and extract
    start time, name, category, (<--mandatory, if missing, disregard event)
    end time, price, address, description, website (<--optional, ok if missing)
    Return a list of dicts that contain this info, one dict per event
    """

    curr_page = 0 # meetup's page offsets start 0, not 1!
    num_shown_so_far = 0
    total_items = 0
    opener = urllib2.build_opener()
    while (curr_page == 0) or (num_shown_so_far < total_items):
        events_list = []
        req = urllib2.Request(("https://api.meetup.com/2/open_events.json?"
                               "radius=0.0&city=Palo+Alto&country=us&state=CA"
                               "&status=upcoming&key=%s&page=%d&offset=%d"
                               % (_MEETUP_KEY, _EVENTS_PER_PAGE, curr_page)))
        try:
        	f = opener.open(req)
        except URLError as e:
        	raise SourceRetrievalError(e.reason)
        	
        meetup_events_dict = json.load(f)
        if 'problem' in meetup_events_dict:
            break

        try:
            total_items = meetup_events_dict['meta']['total_count']
            num_showing = meetup_events_dict['meta']['count']
            num_shown_so_far += num_showing
        except KeyError:
            break

        for ev_dict in meetup_events_dict['results']:
            try:
                name = ev_dict['name']
                categories = [MEET] # TODO categorize better
                start_datetime = datetime.fromtimestamp(
                    float(ev_dict['time'])/1000.0)
            except KeyError:
                continue
            cf_ev_dict = {'name':name, 'categories':categories,
                          'start_datetime':start_datetime}
            _meetup_extract_optional_fields(ev_dict, cf_ev_dict)
            events_list.append(cf_ev_dict)

        curr_page +=1
        yield events_list

def _meetup_extract_optional_fields(ev_dict, cf_ev_dict):
    # No KeyErrors should occur
    if 'duration' in ev_dict and 'time' in ev_dict:
        cf_ev_dict['end_datetime'] = datetime.fromtimestamp(
            (float(ev_dict['time']) + float(ev_dict['duration']))/1000.0)

    if 'fee' in ev_dict:
        if 'amount' in ev_dict['fee']:
            cf_ev_dict['price'] = float(ev_dict['fee']['amount'])
    else:
        cf_ev_dict['price'] = 0

    if 'description' in ev_dict:
        cf_ev_dict['description'] = ev_dict[u'description']

    if 'event_url' in ev_dict:
        cf_ev_dict['url'] = ev_dict['event_url']

    if 'venue' in ev_dict:
            address = ''
            if 'address_1' in ev_dict['venue']:
                address += ev_dict['venue']['address_1']
            if 'address_2' in ev_dict['venue']:
                address += ev_dict['venue']['address_2']
            if 'address_3' in ev_dict['venue']:
                address += ev_dict['venue']['address_3']
            if len(address) > 0:
                cf_ev_dict['address'] = address