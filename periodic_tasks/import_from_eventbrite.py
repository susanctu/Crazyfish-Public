from django.conf import settings
"""settings.configure(
    DATABASES = { 'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_name',
        'USER': 'db_usr',
        'PASSWORD': 'db_pass',
        'HOST': '',
        'PORT': '',
        }, },
    TIME_ZONE = 'Europe/Luxembourg'
)"""
# from events.models import Event, Location, Category
import urllib2 
import json
from sets import Set

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

def get_and_parse_JSON_test():
    gen = get_and_parse_eventbrite_JSON()
    try:
        while True:
            print(next(gen))
    except StopIteration:
        print 'finished' 

def get_cfsite_categories(ebrite_categories):
    """
    Takes a list of eventbrite categories and 
    returns corresponding crazyfish categories.
    """
    cf_categories = Set()
    for cat in ebrite_categories:
        cf_categories.add(EBRITE_TO_CF_CATEGORIES[cat])
    return list(cf_categories)

def get_and_parse_eventbrite_JSON(): # generator function
    """
    Get next page's worth of JSON and extract 
    start time, name, category, place, (<--mandatory, if missing, disregard event)
    end time, price, description, website (<--optional, ok if missing)
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
        
        total_items = ebrite_events_dict[u'events'][0][u'summary'][u'total_items']
        num_showing = ebrite_events_dict[u'events'][0][u'summary'][u'num_showing']
        num_shown_so_far += num_showing

        for i in range(1,num_showing+1):
            try:
                ev_dict =  ebrite_events_dict[u'events'][i][u'event'] 
                name = ev_dict[u'title']
                print ev_dict[u'category'].rsplit(",")
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

def save_to_db(self, list_of_event_dicts): 
    # first call some method to remove duplicates from within the list
    # then save to db (checking that there are no duplicates in the db first)
    gen = get_and_parse_eventbrite_JSON()
    try:
        while True:
            print(next(gen))
    except StopIteration:
        print 'import_from_eventbrite finished'

def import_events(event_generator_fn):
    """
    
    """ 
    pass

if __name__=='__main__':
    get_and_parse_JSON_test()
