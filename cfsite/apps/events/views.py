from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from cfsite.apps.events.models import Location, Category
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
    errors = []
    # Validating event category
    if 'category' in request.GET and request.GET['category']:
        category_name = request.GET['category']
    else:
        errors.append('Please select a category.')

    # Validating date and time field
    if 'date' in request.GET and request.GET['date']:
        date = request.GET['date']
    else:
        errors.append('Please choose a date.')

    # Validating location
    if 'location' in request.GET and request.GET['location']:
        location = request.GET['location']
    else:
        errors.append('Please choose a location.')

    # TODO: replace all this error handling by a SearchForm instance
        
    # If no errors so far, we can proceed with the search
    if not errors:
        return render(request, 'search_results.html')
    # If errors, redirect to the home page.
    else:
        # TODO: add helpful error message code by passing get data in url
        return HttpResponseRedirect('/')
