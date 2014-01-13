__author__ = "Georges Goetz"
__email__ = "ggoetz@stanford.edu"
__status__ = "Prototype"

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
    #if form.errors:
    #    return HttpResponseRedirect('/')

    if form.is_valid():
        event_list = Event.objects.search_for_events(form.get_date(),
                                                     form.get_category_id(),
                                                     form.get_location_id())
        return render(request, 'search_results.html',
                      {'event_list': event_list, })
    # If errors, redirect to the home page.
    else:
        # TODO: add helpful error message code by passing get data in url
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
    @rtype
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