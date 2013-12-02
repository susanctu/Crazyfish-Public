from datetime import datetime
from django import forms
from cfsite.apps.events.models import Category, Location

class SearchForm(forms.Form):
    """ SeachForm
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
        """ SearchForm.clean_category
        ----------
        Make sure that the category selected is among those we have approved.

        """
        if self.category is u'all':
            self.category_id = 0
            return
        else:
            cat_names_and_ids = [(c.id, c.base_name) 
                                 for c in Category.objects.all()]
            matching_id = [cid for (cid, bn) in cat_names_and_ids 
                           if bn == self.category]
            if len(matching_id)>1:
                # If there is more than one match: something went wrong
                raise forms.ValidationError(
                    "The category could not be matched properly.")
            elif matching_id:
                self.category_id = matching_id[0]
                return
            else:
                raise forms.ValidationError("Please choose a valid category.")

    def clean_date(self):
        """ SearchForm.clean_date
        ----------
        Make sure the date is a date, and is after today's date.

        """
        t = datetime.strptime(self.date,"%d/%m/%Y").date()
        now = datetime.now().date()
        if (t < now):
            raise forms.ValidationError("Crazyfish can't help you go back in time.")
        else:
            return

    def clean_location(self):
        """ SearchForm.clean_location
        ----------
        Make sure the location is amongst those we know.

        """
        locations_and_ids = [(l.id, l.city) for l in Location.objects.all()]
        matching_id = [lid for (lid, city) in locations_and_ids
                       if city == self.location]
        if len(matching_id)>1:
            raise forms.ValidationError("Something went wrong when trying to find the location")
        elif matching_id:
            self.location_id = matching_id[0]
            return
        else:
            raise forms.ValidationError("Please choose a location.")

