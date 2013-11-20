from django.shortcuts import render
from django.http import HttpResponse
from books.models import Book

# Create your views here.
def search_events(request):
    errors = []
    errors.append('Search for events not yet implemented.')
    return render(request, 'landing.html', {'errors': errors})
