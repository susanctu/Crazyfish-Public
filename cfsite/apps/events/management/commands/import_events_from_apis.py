import os
import urllib2 
import json
import re
from datetime import datetime
from django.core.management.base import NoArgsCommand, CommandError
from cfsite.apps.events.models import Event, Location, Category
from cfsite.apps.crawlers.deduplication import SimpleDeduplicator

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
                           'travel':FAM, # TODO (susanctu): questionable mapping
                           'religion':FAM, # questionable
                           'fairs':FAM, 
                           'food':FOOD, 
                           'music':MUSIC, 
                           'recreation':FAM}

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
                categories = get_cfsite_categories(ev_dict[u'category'].split(','))
                loc = ev_dict[u'venue'][u'address']
                start_datetime = convert_to_datetime(ev_dict[u'start_date'])
                events_list.append({'name':name, 'categories':categories, 'location':loc, 
                                    'start_datetime':start_datetime})
            except KeyError:
                continue

        yield events_list

 
def get_cfsite_categories(ebrite_categories):
    """
    Takes a list of eventbrite categories and 
    returns corresponding crazyfish categories.
    """
    cf_categories = set()
    for cat in ebrite_categories:
        cf_categories.add(EBRITE_TO_CF_CATEGORIES[cat])
    return list(cf_categories)

    
def convert_to_datetime(ebrite_date_str):
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
    """
    help = 'Pulls events from Eventbrite and adds to database'

    def handle(self, **options):
        self.import_events()

    def save_event_model(self, event_list):
        """
        Save each of the events (represented as dicts)
        in event_list.
        """
        # TODO (susanctu): extend Location class so we can store 
        # a more specific address
        self.stdout.write('Saving events to database:', ending='')
        for event_dict in event_list:
            ev = Event(
                name=event_dict['name'],
                event_location=Location.objects.get_or_create(
                    city='Palo Alto',
                    state_province='CA',
                    zip_code=94301,
                    country='US',
                    timezone='Pacific',
                    )[0], # discard second element (a bool) of tuple
                event_start_date=event_dict['start_datetime'].date(),
                event_start_time=event_dict['start_datetime'].time(),
                is_valid_event=True)

            # TODO (susanctu): should duplicates be at at the same location? 
            if (SimpleDeduplicator.is_duplicate(ev)):
                self.stdout.write('Skipping duplicate...')
            else:
                self.stdout.write(event_dict.__str__())
                ev.save()            
                for category in event_dict['categories']:
                    cat, unused_is_new_bool = Category.objects.get_or_create(base_name=category);
                    ev.category.add(cat);

    def import_events(self): 
        gen = get_and_parse_eventbrite_JSON()
        try:
            while True:
                self.save_event_model(next(gen))
        except StopIteration:
            self.stdout.write('finished') # TODO (susanctu): in future, maybe we want to print some stats  


