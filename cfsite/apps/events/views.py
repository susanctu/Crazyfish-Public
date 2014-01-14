__author__ = "Georges Goetz"
__email__ = "ggoetz@stanford.edu"
__status__ = "Prototype"

import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from cfsite.apps.events.models import Location, Category, Event
from cfsite.apps.events.forms import SearchForm


# Create your views here.
def home(request):
    """ home(request)
    ----------
    View for the home page. 
    Populates the category list with a list of pre approved categories,
    checks if the home page is being rendered because the user entered 
    invalid data, and if so, resets the user's valid data.

    """
    # Set approved list of categories and locations.
    category_list = list(set([c.base_name for c in Category.objects.all()]))
    location_list = list(set([c.city for c in Location.objects.all()]))

    # parse GET request if it exists.
    # If it exists, it comes from a redirect from the search() view, due to
    # invalid user data.
    if request.method == 'GET':
        form = SearchForm(request.GET)
        errors = form.errors
    else:
        errors = {}

    # TODO: update the template so that it can change default value of the
    # different fields.
    # Set the values of the different fields if required.

    # Render.
    return render(request, 'index.html', {'category_list': category_list,
                                          'location_list': location_list,
                                          'error_list': errors})


def search(request):
    """ search(request)
    ----------
    Logic for handling a search request. 
    It will validate the data entered by the user, and if the data is valid,
    look up the list of events which matches the user's request, and render
    them in html.
    If the data is invalid, it will refuse to proceed with the request, and 
    redirect the user to the home search page.

    """
    if request.method == 'GET':
        formatted_request = format_search_get_request(request.GET)
        form = SearchForm(formatted_request)
    else:
        form = SearchForm()

    # If no errors in the form, we can proceed with the search
    if form.is_valid():
        # TODO: what happens if not event?
        event_list = Event.objects.search_for_events(form.get_date(),
                                                     form.get_location_id())

        search_results_data = format_sr_data_from_event_list(event_list)
        return render(request, 'search_results.html',
                      {'sr_data': search_results_data, })
    # If errors, redirect to the home page.
    else:
        return HttpResponseRedirect('/?' + request.GET.urlencode())


# Helper functions underneath
def format_search_get_request(get_request):
    """ format_search_get_request(get_request)
    ----------
    Formats a get request from the index.html into a dictionary the SearchForm
    has a chance of understanding. The date field especially is not formatted
    correctly by default and needs to be changed accordingly.
    For the prototype, this function forces the user to search for 'all' events
    on 'Palo Alto'.

    @param get_request: QueryDict representing the user's GET request.

    @return: dict representing the formatted GET request.
    @rtype: dict
    """
    new_dict = get_request.dict()

    try:
        # Force category to 'all' here
        new_dict[u'category'] = u'all'

        # Force location to 'Palo Alto' here
        new_dict[u'location'] = u'Palo Alto'

        # Format date field here
        date_str = new_dict[u'date'].split(u' ')
        if len(date_str) != 4:
            new_dict[u'date'] = ''
        else:
            month_str_to_num = dict(Jan=1, Feb=2, Mar=3, Apr=4, May=5, Jun=6,
                                    Jul=7, Aug=8, Sep=9, Oct=10, Nov=11,
                                    Dec=12)
            new_dict[u'date'] = date_str[2] + '/' \
                                    + str(month_str_to_num[date_str[1]]) \
                                    + '/' + date_str[3]
    finally:
        return new_dict


def format_sr_data_from_event_list(event_list):
    """ format_sr_data_from_event_list
    ----------
    This function creates the search_results template contextual data from
    a list of events.

    @param event_list: an array of event matching the user's query.
    @type event_list: [Event]
    """
    assert(len(event_list) > 0)

    # unique tab ID: unless the request was made through AJAX, this can be 0
    uid_val = 0

    # format categories for the JS helper
    categories_val = []

    # format event list
    events_val = []

    # format the time header
    # end time is optional, but start time is not, so we only need to filter
    # out None values for t_max.
    t_min = min([event.event_start_time for event in event_list])
    t_max = max(filter(None, [event.event_end_time for event in event_list]))
    e_date = event_list[0].event_start_date
    time_header_val = format_time_header_data_from_min_max(t_min, t_max, e_date)

    # format the lines
    lines_val = [t["pos"] for t in time_header_val["times_val_and_pos"]]

    # Create the final data structure
    sr_data = dict(uid=uid_val, categories=categories_val, events=events_val,
                   time_header=time_header_val, lines=lines_val)
    return sr_data


def format_time_header_data_from_min_max(t_min, t_max, e_date):
    """ format_time_header_data_from_min_max
    ----------
    This function formats the time header data from the smallest start time
    and largest end time existing in an event list.

    @param t_min: minimum start time for all events that are going to be
           displayed
    @type t_min: datetime.time

    @param t_max: maximum end time for all events that are going to be
           displayed
    @type t_max: datetime.time

    @param e_date: date of the search
    @type e_date: datetime.date
    """
    # Set the minimum and maximum values of the time header
    if (t_min.minute == 0) & (t_min.hour > 0):
        t_min.replace(hour=t_min.hour-1)
        t_min.replace(minute=0)
    else:
        t_min.replate(minute=0)

    if t_max.hour == 23:
        t_max.replace(minute=59)
    else:
        t_max.replace(hour=t_max.hour+1)
        t_max.replace(minute=0)
    min_time_val = t_min.strftime('%H:%M')
    max_time_val = t_max.strftime('%H:%M')

    # Format the date string
    weekday_num_to_str = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    month_num_to_str = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                        'Sep', 'Oct', 'Nov', 'Dec']
    date_val = weekday_num_to_str[e_date.weekday()] + ' ' \
               + month_num_to_str[e_date.month] + ' ' + str(e_date.day)

    # Get the lines and their name and position
    times_data_pos = format_lines_data(t_min, t_max)
    all_times_val = []
    for td in times_data_pos:
        all_times_val.append(dict(pos=td,
                                  val=percentage_to_time_string(td,
                                                                t_min, t_max)))

    # Format the time header data
    th_data = dict(min_time=min_time_val, max_time=max_time_val, date=date_val,
                   times_val_and_pos=times_data_pos)

    return th_data


def format_lines_data(t_min, t_max):
    """ format_lines_data
    ----------

    """
    return []


def time_to_percentage(time_val, t_min, t_max):
    """ time_to_percentage
    ----------

    """
    return 0


def percentage_to_time_string(percent, t_min, t_max):
    """ percentage_to_time_string
    ----------

    """
    return ''