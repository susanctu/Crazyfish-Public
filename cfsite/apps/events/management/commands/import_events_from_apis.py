import os
import urllib2
import json
import re
import traceback
import sys
from datetime import datetime
from django.core.management.base import NoArgsCommand, CommandError
from cfsite.apps.events.models import Event, Location, Category
from cfsite.apps.crawlers.deduplication import SimpleDeduplicator

_EBRITE_KEY = "JO34L4OP3GCXGEC2XJ"
_MEETUP_KEY = "6865607a3c4b4d7d52946910646fc"
_EVENTS_PER_PAGE = 100

# the crazyfish categories
_ART = 'arts & culture'
_CLASS = 'classes & workshop'
_CONF = 'conference'
_FAM = 'family'
_SPORT ='sport'
_MUSIC = 'music'
_MEET = 'meetup'
_FOOD = 'food & wine'

CF_CATEGORIES = [_ART, _CLASS, _CONF, _FAM, _MUSIC, _MEET, _FOOD, _SPORT]

EBRITE_TO_CF_CATEGORIES = {'conferences':_CONF,
                           'conventions':_CONF,
                           'entertainment':_ART,
                           'fundraisers':_MEET,
                           'meetings':_MEET,
                           'other':_MEET,
                           'performances':_ART,
                           'reunions':_MEET,
                           'sales':_FAM,
                           'seminars':_CLASS,
                           'social':_MEET,
                           'sports':_SPORT,
                           'tradeshows':_CONF,
                           'travel':_FAM,
                           'religion':_FAM,
                           'fairs':_FAM,
                           'food':_FOOD,
                           'music':_MUSIC,
                           'recreation':_FAM}

def _price_str_to_float(price_str):
    return float(re.sub(u',',u'', price_str))

def _get_and_parse_meetup_JSON(): # generator function
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
        f = opener.open(req)
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
                categories = [_MEET] # TODO categorize better
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


def _get_and_parse_eventbrite_JSON(): # generator function
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
        f = opener.open(req)
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
        cf_categories.add(EBRITE_TO_CF_CATEGORIES[cat])
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


class Command(NoArgsCommand):
    """
    Note that many of the methods in here could have been written as
    functions or static methods, but we pass in self since the
    documentation for custom manage.py commands says that we should
    use self.stdout.write instead of printing directly to stdout.
    TODO (susanctu): why? possibly rethink this
    """
    help = 'Pulls events from Eventbrite and adds to database'

    def handle(self, **options):
        self._import_events()

    def _save_event_model(self, event_list):
        """
        Save each of the events (represented as dicts)
        in event_list.
        """
        self.stdout.write('Saving events to database:')
        for event_dict in event_list:
            ev = Event(
                name=event_dict['name'],
                event_location=Location.objects.get_or_create(
                    city='Palo Alto',
                    state_province='CA',
                    zip_code=94303,
                    country='United States',
                    timezone='US/Pacific',
                    )[0], # discard second element (a bool) of tuple
                event_start_date=event_dict['start_datetime'].date(),
                event_start_time=event_dict['start_datetime'].time(),
                is_valid_event=True)

            if 'end_datetime' in event_dict:
                ev.event_end_date = event_dict['end_datetime'].date()
                ev.event_end_time = event_dict['end_datetime'].time()
            if 'price' in event_dict:
                ev.price = event_dict['price']
            if 'url' in event_dict:
                ev.website = event_dict['url']
            if 'description' in event_dict:
                ev.description = event_dict['description']
            if 'address' in event_dict:
                ev.address = event_dict['address']

            if (SimpleDeduplicator.is_duplicate(ev)):
                self.stdout.write('Skipping duplicate...')
            else:
                self.stdout.write(event_dict['name'])
                ev.save()
                for category in event_dict['categories']:
                    cat, unused_is_new_bool = Category.objects.get_or_create(base_name=category);
                    ev.category.add(cat);

    def _import_events(self):
        gens = [_get_and_parse_meetup_JSON(), _get_and_parse_eventbrite_JSON()]
        for gen in gens:
            try:
                while True:
                    self._save_event_model(next(gen))
            except StopIteration:
                self.stdout.write('...Finished pulling from one data source') # TODO (susanctu): in future, maybe we want to print some stats


