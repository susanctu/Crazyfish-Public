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

    # TODO: parse GET request if it exists.


    # TODO: update the template so that it can change default value of the
    # different fields. 
    # Set the values of the different fields if required.

    # Render.
    return render(request, 'index.html', {'category_list': category_list,
                                          'location_list': location_list,})


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
        form = SearchForm(request.GET)
    else:
        form = SearchForm()

    # If no errors in the form, we can proceed with the search
    if not form.errors:
        event_list = Event.objects.search_for_events(form.get_date(),
                                                     form.get_category_id(),
                                                     form.get_location_id())
        return render(request, 'search_results.html', 
                      {'event_list': event_list, })
    # If errors, redirect to the home page.
    else:
        # TODO: add helpful error message code by passing get data in url
        return HttpResponseRedirect('/')
