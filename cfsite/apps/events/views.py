__author__ = "Georges Goetz"
__email__ = "ggoetz@stanford.edu"
__status__ = "Prototype"

import datetime, math
from django.shortcuts import render
from django.http import HttpResponseRedirect
from cfsite.apps.events.models import Location, Category, Event
from cfsite.apps.events.forms import SearchForm
from cfsite.apps.crawlers.parsers import MLStripper, MLTagDetector, MLFormatter

# Category logo and verbose names
CAT_LOGO_NAME = []
CAT_VERBOSE_NAME = []


# The event related views are here.
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
        # TODO: what happens to template if no event?
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

    @return: the search_results template contextual data.
    @rtype: dict
    """
    # unique tab ID: unless the request was made through AJAX, this can be 0
    uid_val = 0

    # format categories for the JS helper
    categories_val = build_category_data(
        list(set([c.id for c in Category.objects.all()]))
    )

    if event_list:
        # for everything: need to know what limits of the time filter are
        t_min = min([event.event_start_time for event in event_list])
        # end time is optional, but start time is not, so we only need to filter
        # out None values for t_max.
        # t_max can also be the maximum event start time of an event that does not
        # have duration information
        t_max1 = max([event.event_start_time for event in event_list])
        t_max2 = max(filter(None, [event.event_end_time for event in event_list]))
        t_max = max([t_max1, t_max2])

        # format event list
        events_val = []
        for event in event_list:
            events_val.append(format_event_data(event, t_min, t_max))

        # format the time header
        e_date = event_list[0].event_start_date
        time_header_val = format_time_header_data_from_min_max(t_min, t_max, e_date)

        # format the lines
        lines_val = [t["pos"] for t in time_header_val["times_val_and_pos"]]
    else:
        # TODO
        events_val = []
        time_header_val = []
        lines_val = []

    # Create the final data structure
    sr_data = dict(uid=uid_val, categories=categories_val, events=events_val,
                   time_header=time_header_val, lines=lines_val)
    return sr_data


def format_event_data(event, t_min, t_max):
    """ format_event_data(event, t_min, t_max)
    ----------
    Formats the data from a single event into a dictionary that can be used
    to render correctly event data.

    @param event: an Event object.
    @type event: Event

    @param t_min: minimum time that is displayed on the time slider control
    @type t_min: datetime.time

    @param t_max: maximum time displayed on the time slider control
    @type t_max: datetime.time
    """
    # First thing to do: format the description string.
    # Strip the HTML tags from the description for the preview
    if event.description:
        s = MLStripper()
        s.feed(event.description)
        description_short_val = s.get_data()[0:100]
        # Detect if description is HTML or not
        t_detect = MLTagDetector()
        t_detect.feed(event.description)
        if not t_detect.get_tags():
            # If not tags, it is not and need to be formatted.
            formatter = MLFormatter()
            formatter.feed(event.description)
            description_formatted_val = formatter.get_formatted_string()
        else:
            description_formatted_val = event.description
    else:
        description_short_val = 'No description for this event.'
        description_formatted_val = '<p>No description for this event.</p>'

    # Then: format start, end time, duration
    start_time_val = event.event_start_time.strftime('%H:%M')
    start_time_val_percent = time_to_percentage(
        event.event_start_time, t_min, t_max
    )
    [duration_minutes_val, duration_str_val, duration_percent_val] = \
        duration_from_start_end_time(
            event.event_start_time, event.event_end_time, t_min, t_max
        )

    # Format the datetime string for display purposes
    weekday_num_to_str = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    month_num_to_str = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                        'Sep', 'Oct', 'Nov', 'Dec']
    datetime_val = weekday_num_to_str[event.event_start_date.weekday()] + ' ' \
                   + month_num_to_str[event.event_start_date.month] + ' ' \
                   + str(event.event_start_date.day) + ', ' + start_time_val

    # Check if price is here or not
    if event.price:
        price_val = event.price
    else:
        price_val = '??'

    # Format the category data
    cat_data = build_category_data(event.category)

    # Build the final event template context dictionary
    ecd = dict(
        category_list=event.category,
        rating=event.rating,
        name=event.name,
        description_short=description_short_val,
        description_formatted=description_formatted_val,
        event_start_time=start_time_val,
        event_start_time_percent=start_time_val_percent,
        duration=duration_str_val,
        duration_minutes=duration_minutes_val,
        duration_percent=duration_percent_val,
        price=price_val,
        event_date_time_verbose=datetime_val,
        category_logo=cat_data,
    )

    if event.website:
        ecd['website'] = event.website
    if event.price_details:
        ecd['price_details'] = event.price_details
    if event.address:
        ecd['address'] = event.address

    return ecd


def format_time_header_data_from_min_max(t_min, t_max, e_date):
    """ format_time_header_data_from_min_max(t_min, t_max, e_date)
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

    @return: the time_header contextual data
    @return: dict
    """
    # Set the minimum and maximum values of the time header
    [t_min, t_max] = calculate_bounds_time_data(t_min, t_max)
    min_time_val = t_min.strftime('%H:%M')
    if t_max == datetime.time(23, 59):
        max_time_val = '24:00'
    else:
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
        all_times_val.append(
            dict(pos=td, val=percentage_to_time_string(td, t_min, t_max))
        )

    # Format the time header data
    th_data = dict(min_time=min_time_val, max_time=max_time_val, date=date_val,
                   times_val_and_pos=times_data_pos)

    return th_data


def calculate_bounds_time_data(t_min, t_max):
    """ calculate_bounds_time_data(t_min, t_max)
    ----------
    Calculates the bounds of the time header from the minimum event start
    time and maximum event end time.

    @param t_min: minimum event start time
    @type t_min: datetime.time

    @param t_max: maximum event end time
    @type t_max: datetime.time

    @return: the minimum and maximum times that will be used for the time
             header slider control.
    @rtype: [datetime.time(), datetime.time()]
    """
    # First: start by broadening the time range to guarantee all events
    # fit into the window.
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

    # Then make sure the width of the window is a multiple of two hours
    # 23:59 for t_max is a special case, as it should really be 24:00
    if t_max == datetime.time(23, 59):
        if divmod(24 - t_min.hour, 2):
            t_min.replace(hour=t_min.hour-1)
    else:
        if divmod(24 - t_min.hour, 2):
            if t_max.hour == 23:
                t_max.replace(minute=59)
            else:
                t_max.replace(hour=t_max.hour+1)

    return [t_min, t_max]


def format_lines_data(t_min, t_max):
    """ format_lines_data(t_min, tmax)
    ----------
    Creates the set of vertical lines which will be used as delimiters on the
    search_results page.

    @param t_min: minimum time allowed on the time slider control.
    @type t_min: datetime.time

    @param t_max: maximum time allowed on the time slider control.
    @type t_max: datetime.time

    @return: array of percentages representing the position of the lines.
    @rtype: [float]
    """
    # We're going to work with minutes
    if t_max == datetime.time(23, 59):
        t_max = 24*60
    else:
        t_max = t_max.hour*60 + t_max.minute
    t_min = t_min.hour*60 + t_min.minute

    # Determine if we're doing 30min, 1h or 2h intervals
    # Interval is two hours: do 30min intervals
    if t_max-t_min <= 120:
        interval = 30
    # Interval is 4 hours: do 60 minutes intervals
    elif t_max-t_min <= 240:
        interval = 60
    # Otherwise, do 120 minutes intervals
    else:
        interval = 120

    # Create the lines accordingly
    line_pos = []
    c_pos = t_min + interval
    while c_pos < t_max:
        line_pos.append(round((c_pos-t_min)/(t_max-t_min)*100, 1))
        c_pos += interval

    return line_pos


def build_category_data(cat_id_list):
    """ build_category_data
    ----------

    @param cat_id_list: a list of categories IDs
    @type cat_id_list: [int]
    """
    # TODO
    return []


def time_to_percentage(time_val, t_min, t_max):
    """ time_to_percentage(time_val, t_min, t_max)
    ----------
    Converts a time value into a percentage of the time bar, as delimited
    by t_min and t_max.
    If time_val is outside the range of values allowed, it is rounded to 0
    or 100.

    @param time_val: value that is going to be converted into a percentage
    @type time_val: datetime.time()

    @param t_min: minimum time displayed on the time bar
    @type t_min: datetime.time()

    @param t_max: maximum time displayed on the time bar
    @type t_max: datetime.time()

    @return: a percentage of the time bar, rounded to 1 digit
    @rtype: float
    """
    # Convert everything to minutes, with the caveat that 23:59 for t_max
    # actually means 24:00.
    if t_max == datetime.time(23, 59):
        t_max = 24*60
    else:
        t_max = t_max.hour*60 + t_max.minute
    t_min = t_min.hour*60 + t_min.minute
    time_val = time_val.hour*60 + time_val.minute

    # Then: to percentage
    percentage = round((time_val-t_min)/(t_max-t_min)*100, 1)
    if percentage < 0:
        percentage = 0
    if percentage > 100:
        percentage = 100

    return percentage


def percentage_to_time_string(percent, t_min, t_max):
    """ percentage_to_time_string(percent, t_min, t_max)
    ----------
    Converts a percentage representing

    @param percent: the percentage (between 0 and 100) which is going to be
           converted to a time string.
    @type percent: float

    @param t_min: minimum time allowed on the time bar.
    @type t_min: datetime.time

    @param t_max: maximum time allowed on the time bar.
    @type t_max: datetime.time

    @return: time string corresponding to the percentage.
    @rtype: str
    """
    # Going to minutes...
    if t_max == datetime.time(23, 59):
        t_max = 24*60
    else:
        t_max = t_max.hour*60 + t_max.minute
    t_min = t_min.hour*60 + t_min.minute

    new_time = round(t_min + (t_max-t_min)/(percent/100))
    new_time = datetime.time(
        int(math.floor(new_time/60)),
        int(new_time - math.floor(new_time/60)*60)
    )

    return new_time.strftime('%H:%M')


def duration_from_start_end_time(start_time, end_time, t_min, t_max):
    """ duration_from_start_end_time
    ----------

    @param start_time

    @param end_time

    @param t_min

    @param t_max

    @return: an array with duration in minutes,
    @rtype:
    """
    # TODO
    return ['','','']