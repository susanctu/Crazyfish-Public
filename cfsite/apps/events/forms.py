__author__ = "Georges Goetz"
__email__ = "ggoetz@stanford.edu"
__status__ = "Prototype"

import pytz
from datetime import datetime
from django import forms
from cfsite.apps.events.models import Category, Location


class SearchForm(forms.Form):
    """ SearchForm
    ----------
    A class which handles user search data.
    It mostly takes care of validating user input.

    """
    category = forms.CharField()
    category_id = forms.IntegerField(required=False)
    date = forms.DateField()
    location = forms.CharField()
    location_id = forms.IntegerField(required=False)

    def clean_category(self):
        """ SearchForm.clean_category()
        ----------
        Make sure that the category selected is among those we have approved.

        """
        category = self.cleaned_data['category']

        if category != u'all':
            matching_ids = get_all_matching_category_ids(category)
            if len(matching_ids)>1:
                # If there is more than one match: something went wrong
                raise forms.ValidationError(
                    "Ooops. We couldn't understand what type of events you're looking for.")
            elif not matching_ids:
                raise forms.ValidationError("We don't have data for this type of events.")

        return category

    def clean_location(self):
        """ SearchForm.clean_location()
        ----------
        Make sure the location is amongst those we know.

        """
        location = self.cleaned_data['location']

        matching_ids = get_all_matching_location_ids(location)
        if len(matching_ids) > 1:
            raise forms.ValidationError("Ooops. We couldn't understand which location you're interested in.")
        elif not matching_ids:
            raise forms.ValidationError("Crazyfish is not available at the location specified.")

        return location

    def clean(self):
        """ SearchForm.clean()
        ----------
        After all the user inputs have been validated, this function will
        fill in the category and location ID from the valid location and
        category data.
        These IDs can then be used to search matching events.
        Note: there is no need to verify a single ID is returned by the
        functions get_category_ids and get_location_ids, because this
        check already happened in the location and category validation methods.

        After IDs have been validated, the date is cleaned. This cannot be done
        before as it needs to know in which time zone the location is in
        order to check things properly.

        """

        # First, check that something hasn't gone wrong already.
        if self.errors:
            return {}

        # Cleaning IDs
        category_name = self.cleaned_data['category']
        if category_name != u'all':
            matching_category_ids = get_all_matching_category_ids(
                category_name
            )
            self.cleaned_data['category_id'] = matching_category_ids[0]
        else:
            self.cleaned_data['category_id'] = 0

        location_name = self.cleaned_data['location']
        matching_location_ids = get_all_matching_location_ids(
            location_name)
        self.cleaned_data['location_id'] = matching_location_ids[0]
        location = Location.objects.get(id=matching_location_ids[0])

        # Cleaning date
        t = self.cleaned_data['date']
        now = datetime.now(pytz.timezone(location.timezone)).date()
        if t < now:
            raise forms.ValidationError("It looks like the date you searched for already happened...")

        return self.cleaned_data

    def get_location(self):
        """ SearchForm.get_location()
        ---------
        Returns the name of the location macthing the user's request from
        the cleaned form data.

        """
        return self.cleaned_data['location']

    def get_location_id(self):
        """ SearchForm.get_location_id()
        ----------
        Returns the location id matching the user's request from the
        cleaned form data.

        """
        return self.cleaned_data['location_id']

    def get_category_id(self):
        """ SearchForm.get_gategory_id()
        ----------
        Returns the category id matching the user's request from the cleaned
        form data.

        """
        return self.cleaned_data['category_id']

    def get_date(self):
        """ SearchForm.get_date()
        ----------
        Returns the date if the field passed validation.

        """
        return self.cleaned_data['date']


def get_all_matching_category_ids(category_name):
    """ SearchForm.get_all_matching_category_ids(category_name)
    ----------
    This function returns a list (possibly empty) of category ids matching
    a category name.

    """
    category_list = Category.objects.filter(
        base_name__icontains=category_name
    ).all()
    return [category.id for category in category_list]


def get_all_matching_location_ids(location_name):
    """ SearchForm.get_all_matching_location_ids(location_name)
    ----------
    This function returns a list (possibly empty) of location ids matching
    a location name

    """
    locations_list = Location.objects.filter(
        city__icontains=location_name
    ).all()
    return [location.id for location in locations_list]
