import os
import urllib2
from urllib2 import URLError
import json
import re
from xml.dom import minidom
from datetime import datetime
from cfsite.apps.events.models import MEET, SPORT, ART, FAM
from cfsite.apps.crawlers.management.commands._errors import SourceRetrievalError

DAYS = ['Mondays','Tuesdays','Wednesdays','Thursdays','Fridays','Saturdays','Sundays']

def _get_basic_info_assume_pubDate_reliable(event_xml, process_datetime_fn):
    """
    Takes in xml for an event and a functional that will be used to cleanup 
    data in the 'pubDate' element.

    Returns dictionary with name, start_datetime, and description on success, 
    returns None if unable to obtain any one of these mandatory pieces of info
    """
    try: 
        name = event_xml.getElementsByTagName('title')[0].firstChild.data
        description = event_xml.getElementsByTagName('description')[0].firstChild.data
        start_datetime_str = event_xml.getElementsByTagName('pubDate')[0].firstChild.data
    except IndexError:
        return None

    try:
        start_datetime = process_datetime_fn(start_datetime_str)
    except ValueError: # datetime string did not match expected format
        return None
    cf_ev_dict = {'name':name, 
                  'start_datetime':start_datetime,
                  'description': description}
    return cf_ev_dict

def _get_basic_info_unreliable_pubDate(event_xml, get_datetime_fn):
    try: 
        name = event_xml.getElementsByTagName('title')[0].firstChild.data
        description = event_xml.getElementsByTagName('description')[0].firstChild.data
    except IndexError:
        return None

    try:
        start_datetime = get_datetime_fn(description) # TODO (susanctu) possibly show the event multiple times
    except ValueError: # datetime string did not match expected format
        return None
    cf_ev_dict = {'name':name, 
                  'start_datetime':start_datetime,
                  'description': description}
    return cf_ev_dict

def get_and_parse_paloaltoplayers():
    xmldoc = _get_xml_doc("http://www.paplayers.org/feed/my-calendar-rss")

    itemlist = xmldoc.getElementsByTagName('item')
    event_list = []
    for item in itemlist:
        cf_ev_dict = _get_basic_info_unreliable_pubDate(item, _extract_datetime_paloaltoplayers)
        if not cf_ev_dict:
            continue
        cf_ev_dict['categories'] = [ART]
        _get_optional_link(item, cf_ev_dict)
        event_list.append(cf_ev_dict)

    yield event_list

def _extract_datetime_paloaltoplayers(description):
    """
    Within |description|, attempts to find dates of the following form:

        April 26 - May 11, 2014, preview April 25
        Thursdays - Saturdays at 8pm 
        and Sundays at 2:30pm

    Returns a list of datetime.datetime objects indicating start times 
    TODO right now this only returns the first datetime
    """
    start_date_pattern  = re.compile("(January|February|March|April|May|June|July|August"
                                         "|September|October|November|December)\W\d{1,2}")
    stripped_start_date = start_date_pattern.search(description)
    
    if not stripped_start_date:
        raise ValueError('Could not find date string in expected format')
    else:
        day_of_week = datetime.strptime("%s 2014" % stripped_start_date.group(), "%B %d %Y").weekday()

    day_or_day = '|'.join(DAYS)
    start_time_patterns  = (re.compile("(%s)\W.\W(%s)\Wat\W(\d+:?\d*(am|pm))" % (day_or_day, day_or_day)),
                            re.compile("and\W(%s)\Wat\W(\d+:?\d*(am|pm))" % day_or_day))

    most_days = start_time_patterns[0].search(description)
    one_days = start_time_patterns[1].search(description)
    
    # check if the earlier day (in sense of Monday being "earlier" than Tuesday) 
    # is listed first
    if most_days:
        if DAYS.index(most_days.group(1)) < DAYS.index(most_days.group(2)):
            earlier_day = DAYS.index(most_days.group(1))
            later_day = DAYS.index(most_days.group(2))
        else:
            later_day = DAYS.index(most_days.group(2))
            earlier_day = DAYS.index(most_days.group(1))

    if most_days and day_of_week >= earlier_day and day_of_week <= later_day:
        if ':' in most_days.group(3):
            return datetime.strptime("%s 2014 %s" % (stripped_start_date.group(), most_days.group(3)), "%B %d %Y %I:%M%p")
        else:
            return datetime.strptime("%s 2014 %s" % (stripped_start_date.group(), most_days.group(3)), "%B %d %Y %I%p")
    elif one_day and day_of_week == DAYS.index(one_day.group(1)):
        if ':' in one_day.group(2):
            return datetime.strptime("%s 2014 %s" % (stripped_start_date.group(), one_day.group(2)), "%B %d %Y %I:%M%p")
        else:
            return datetime.strptime("%s 2014 %s" % (stripped_start_date.group(), one_day.group(2)), "%B %d %Y %I%p")
    else:
        raise ValueError('Could not find time string in expected format')

def get_and_parse_cityofpaloalto(): # generator function
    xmldoc = _get_xml_doc("http://www.cityofpaloalto.org/custom/whatsnew_rss1.asp")

    itemlist = xmldoc.getElementsByTagName('item')
    event_list = []
    for item in itemlist:
        cf_ev_dict = _get_basic_info_assume_pubDate_reliable(item, _convert_to_datetime_cityofpaloalto)
        if not cf_ev_dict:
            continue
        cf_ev_dict['categories'] = [FAM]
        _get_optional_link(item, cf_ev_dict)
        event_list.append(cf_ev_dict)

    yield event_list

def _convert_to_datetime_cityofpaloalto(start_datetime_str):
    """
    Takes a date/time in the form:
        Sat, 25 Jan 2014 19:00:00 -0800

    Removes the unnecessary info at the beginning and end and returns 
    a datetime.datetime object.
    """
    start_datetime_pattern  = re.compile("\d+\W[a-zA-Z]+\W\d+\W\d+:\d+")
    stripped_start_datetime = start_datetime_pattern.search(start_datetime_str)
    if not stripped_start_datetime:
        raise ValueError('Could not find datetime string in expected format')
    return datetime.strptime(stripped_start_datetime.group(), "%d %b %Y %H:%M")

def get_and_parse_stanford_sport(): # generator function
    """
    Get xml from the rss feed, parse it 
    start time, name, category, description (<--mandatory, if missing, disregard event)
    website (<--optional, ok if missing)
    Return a list of dicts that contain this info, one dict per event
    """
    xmldoc = _get_xml_doc("http://www.gostanford.com/rss.dbml?db_oem_id=30600&media=schedules")

    itemlist = xmldoc.getElementsByTagName('item')
    event_list = []
    for item in itemlist:
        cf_ev_dict = _get_basic_info_assume_pubDate_reliable(item, _convert_to_datetime_stanford_sport)
        if not cf_ev_dict or not "Stanford, CA" in cf_ev_dict['description']: # only show home games
            continue 
        cf_ev_dict['categories'] = [SPORT]
        _get_optional_link(item, cf_ev_dict)

        event_list.append(cf_ev_dict)

    yield event_list

def _get_optional_link(event_xml, cf_ev_dict):
    try:
        url = event_xml.getElementsByTagName('link')[0].firstChild.data
        cf_ev_dict['url'] = url
    except IndexError:
        pass # don't do anything since url was an optional field

def _convert_to_datetime_stanford_sport(start_datetime_str):
    """
    Takes in a date of the following format:
        01/30/2014 08:00 PM

    Returns a datetime.datetime object
    """
    return datetime.strptime(start_datetime_str, "%m/%d/%Y %I:%M %p ")

def _convert_to_datetime_stanford_general(date_str, time_str):
    """
    Takes a date_str of the following format:
        "January 23, 2014"
    Day of month need not be 0 padded.

    time_str should be of the format "4:15 PM"

    Returns a datetime.datetime object.
    """
    return datetime.strptime(date_str + ' ' + time_str, "%B %d, %Y %I:%M %p")

def _get_xml_doc(url):
    """
    Takes a in a url (string) that there is an xml document at.

    Returns the xml.
    """
    opener = urllib2.build_opener()
    req = urllib2.Request(url)
    try:
        f = opener.open(req)
    except URLError as e:
        raise SourceRetrievalError(e.reason)
    
    return minidom.parse(f)

def get_and_parse_stanford_general(): # generator function
    """
    Get xml from the rss feed, parse it 
    start time, name, category, description (<--mandatory, if missing, disregard event)
    website (<--optional, ok if missing)
    Return a list of dicts that contain this info, one dict per event
    """
    
    xmldoc = _get_xml_doc("http://events.stanford.edu/xml/byCategory/0/rss.xml")

    itemlist = xmldoc.getElementsByTagName('item')
    
    start_date_pattern = re.compile("(January|February|March|April|May|June|July|August"
                                    "|September|October|November|December)\W\d{1,2}[,\W]+\d{4}")

    start_time_pattern = re.compile("\d{1,2}:\d{2}\W(AM|PM)")
    event_list = []
    for item in itemlist:
        try: 
            name = item.getElementsByTagName('title')[0].firstChild.data
            description = item.getElementsByTagName('description')[0].firstChild.data
        except IndexError:
            continue # move onto the next event
        categories = [ART] # do something smarter with the description

        # can't use pubDate for this feed
        start_date = start_date_pattern.search(description)
        start_time = start_time_pattern.search(description)

        if not start_date or not start_time:
            continue # unable to extract mandatory info
        else:
            start_date = start_date.group()
            start_time = start_time.group()

        start_datetime = _convert_to_datetime_stanford_general(start_date, start_time)
        cf_ev_dict = {'name':name, 'categories':categories,
                      'start_datetime':start_datetime,
                      'description': description}

        _get_optional_link(item, cf_ev_dict)

        event_list.append(cf_ev_dict)

    yield event_list
