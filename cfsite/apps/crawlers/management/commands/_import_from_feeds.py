import os
import urllib2
from urllib2 import URLError
import json
import re
from xml.dom import minidom
from datetime import datetime
from cfsite.apps.events.models import MEET, SPORT
from cfsite.apps.crawlers.management.commands._errors import SourceRetrievalError

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
        try: 
            name = item.getElementsByTagName('title')[0].firstChild.data
            description = item.getElementsByTagName('description')[0].firstChild.data
            start_datetime_str = item.getElementsByTagName('pubDate')[0].firstChild.data
        except IndexError:
            continue # move onto the next event
        categories = [SPORT] # do something smarter with the description

        if not "Stanford, CA" in description:
            continue # only show home games

        try:
            start_datetime = _convert_to_datetime_stanford_sport(start_datetime_str)
        except ValueError: # datetime string did not match expected format
            continue # move onto the next event

        cf_ev_dict = {'name':name, 'categories':categories,
                      'start_datetime':start_datetime,
                      'description': description}
        try:
            url = item.getElementsByTagName('link')[0].firstChild.data
            cf_ev_dict['url'] = url
        except IndexError:
            pass # don't do anything since url was an optional field

        event_list.append(cf_ev_dict)

    yield event_list

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
        categories = [MEET] # do something smarter with the description

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
        try:
            url = item.getElementsByTagName('link')[0].firstChild.data
            cf_ev_dict['url'] = url
        except IndexError:
            pass # don't do anything since url was an optional field

        event_list.append(cf_ev_dict)

    yield event_list
