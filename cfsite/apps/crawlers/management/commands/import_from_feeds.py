import os
import urllib2
import json
from datetime import datetime
from cfsite.apps.events.models import MEET
from import_events import SourceRetrievalError

def _convert_to_datetime_stanford_general(date_str, time_str=None):
    """
    Takes a date_str of the following format:
        "January 23, 2014"
    Day of month need not be 0 padded.

    time_str, if provided, should be of the format "4:15 PM"

    Returns a datetime.datetime object.
    """
    if not time_str:
        return datetime.strptime(date_str, "%B %d, %Y")
    else: 
        return datetime.strptime(date_str + ' ' + time_str, "%B %d, %Y %I:%M %p")

def get_and_parse_stanford_general(): # generator function
    """
    Get xml from the rss feed, parse it 
    start time, name, category, (<--mandatory, if missing, disregard event)
    end time, price, address, description, website (<--optional, ok if missing)
    Return a list of dicts that contain this info, one dict per event
    """

    opener = urllib2.build_opener()
    req = urllib2.Request(
        "http://events.stanford.edu/xml/byCategory/0/rss.xml")
    try:
        f = opener.open(req)
    except URLError as e:
        raise SourceRetrievalError(e.reason)
    
    xmldoc = minidom.parse(f)

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

        start_date = start_date_pattern.search(description)
                                    
        if not start_date:
            continue # unable to extract mandatory info
        else:
            start_date = start_date.group()

        start_time = start_time_pattern.search(description)

        if start_time:
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
