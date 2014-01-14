import os
import urllib2 
import json
from datetime import datetime
from django.core.management.base import NoArgsCommand, CommandError
from cfsite.apps.events.models import Event, Location, Category

APP_KEY = "JO34L4OP3GCXGEC2XJ"

# the crazyfish categories
ART = 'arts & culture'
CLASS = 'classes & workshop'
CONF = 'conference'
FAM = 'family'
SPORT ='sport'
MUSIC = 'music'
MEET = 'meetup'
FOOD = 'food & wine'
EBRITE_TO_CF_CATEGORIES = {'conferences':CONF, 
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
                           'fairs':FOOD, 
                           'food':FOOD, 
                           'music':MUSIC, 
                           'recreation':FAM}

# TODO (susanctu): fix this first thing tomorrow!
def get_cfsite_categories(ebrite_categories):
    """
    Takes a list of eventbrite categories and 
    returns corresponding crazyfish categories.
    """
    cf_categories = set()
    for cat in ebrite_categories:
        cf_categories.add(EBRITE_TO_CF_CATEGORIES[cat])
    return list(cf_categories)

def get_and_parse_eventbrite_JSON(): # generator function
    """
    Get next page's worth of JSON and extract 
    start time, name, category, place, (<--mandatory, if missing, disregard event)
    TODO (susanctu): end time, price, description, website (<--optional, ok if missing)
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
                               "?app_key=%s&city=Palo+Alto&region=CA&max=100&page=%d" 
                               % (APP_KEY, curr_page)))
        f = opener.open(req)
        ebrite_events_dict = json.load(f)
        if u'error' in ebrite_events_dict:
            break
       
        # TODO (susanctu): what if the next two lines result in KeyError? 
        total_items = ebrite_events_dict[u'events'][0][u'summary'][u'total_items']
        num_showing = ebrite_events_dict[u'events'][0][u'summary'][u'num_showing']
        num_shown_so_far += num_showing

        for i in range(1,num_showing+1):
            try:
                ev_dict =  ebrite_events_dict[u'events'][i][u'event'] 
                name = ev_dict[u'title']
                categories = get_cfsite_categories(ev_dict[u'category'].rsplit(','))
                loc = ev_dict[u'venue'][u'address']
                start_time = ev_dict[u'start_date']
                events_list.append({'name':name, 'categories':categories, 'location':loc, 
                                    'start_time':start_time})
            except KeyError:
                continue

        yield events_list
         

def get_and_parse_meetup_JSON():
    pass

def save_event_model(event_list):
    """
    Save each of the events (represented as dicts)
    in event_list.
    Currently the only piece of info from the dict that 
    is saved is the event name. (other fields are filled in with dummy info)
    """
    for event_dict in event_list:
        ev = Event(
            name=event_dict['name'],
            event_location=Location.objects.get_or_create(
                city='Palo Alto',
                state_province='CA',
                zip_code=94301,
                country='US',
                timezone='Pacific',
                )[0],
            event_start_date=datetime.now().today(),
            event_start_time=datetime.now().time(),
            is_valid_event=True)
        cat, unused_is_new_bool = Category.objects.get_or_create(base_name=MEET);
        ev.save()
        ev.category.add(cat);

def import_events(): 
    gen = get_and_parse_eventbrite_JSON()
    try:
        while True:
            # TODO (susanctu): first call some method to remove duplicates from within the list
            # then save to db (checking that there are no duplicates in the db first)
            save_event_model(next(gen))
    except StopIteration:
        return 'finished' # TODO (susanctu): in future, maybe we want to return some stats  

class Command(NoArgsCommand):
    help = 'Pulls events from Eventbrite and adds to database'

    def handle(self, **options):
        result_msg = import_events()
        self.stdout.write(result_msg)
