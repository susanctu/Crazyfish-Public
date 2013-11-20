import datetime
from django.db import models
from django.core.exceptions import ValidationError

### Models for the event app here ###

# Location model here
class Location(models.Model):
    city = models.CharField(max_length=60)
    state_province = models.CharField('state or province', max_length=30,
                                      blank=True)
    country = models.CharField(max_length=50)
    zip_code = models.PositiveIntegerField(max_length=5)

    """ Location.__unicode__
    ----------
    Defines the formatting of a Location

    """
    def __unicode(self):
        return self.city

    """ Location.clean()
    ----------
    Custom validation method, which runs the following checks: 
        - if state_or_province is stripped if country is not "U.S.A." 
        or "Canada"
        - if country is USA or Canada, then the state_or_province should be 
        provided

    """
    def clean(self):
        # Dont allow events happening in CA or USA to not have a state or
        # province
        if self.country == 'U.S.A' or self.country == 'Canada':
            if not self.state_province:
                raise ValidationError(
                    'Events in the USA or Canada must have a state or province')
        # For events outside these two countries, strip the state or province.
        else:
            self.state_province = ""

    class Meta:
        ordering = ['zip_code']


# Event model here...
""" Event model class
----------
This class represents a model for the event stored in the database. 
An event is primarily comprised of a name and category. It also needs a time 
and place for it to be valid. 
Optionally, an event can have a price, a description and a website.

An event can have a different start date from its end date (required for events
which last more than a day, for exmple a music festival). 
When the end date and time of and event are not specified, the event is assumed
to end an hour after its initial start time. If an event end date is specified
but not the event end hour, the event will be assumed to end at midnight on 
this day.
"""
class Event(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True)
    event_location = models.ForeignKey(Location)
    address = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    event_start_date = models.DateField('start date')
    event_end_date = models.DateField('end date, optional',
                                      blank=True, null=True)
    event_start_time = models.TimeField('start time')
    event_end_time = models.TimeField('end time', blank=True, null=True)
    price = models.FloatField(blank=True, null=True)

    """ Event.__unicode__
    ----------
    Defines the formatting of an event

    """
    def __unicode__(self):
        return self.name
    
    """ Event.clean()
    ----------
    Custom model validation, which runs the following sanity checks:
        - price should be always be positive
        - event start time should be before event end time.
   
    """
    def clean(self):
        # Price should always be positive
        if self.price is not None and self.price<0:
            raise ValidationError('Price cannot be negative')
        
        # Plug in default values if end date and end time weren't specified
        # If the end date was specified, the end time could be implied.
        if self.event_end_date is not None and self.event_end_time is None:
            self.event_end_time.hours = datetime.time(23,59,0)
        if self.event_end_date is None:
            self.event_end_date = self.event_start_date

        # Default event duration is 1 hour
        if self.event_end_time is None:
            self.event_end_time = self.event_start_time
            if self.event_start_time.hour == 23:
                self.event_end_time.hours = 0
                self.event_end_date += datetime.timedelta(days=1)
            else:
                self.event_end_time.hours += 1

        # Check that start and end date and time of the event are consistent
        if self.event_end_date < self.event_start_date:
            raise ValidationError('Start and end dates are inconsistent.')
        elif self.event_end_date == self.event_start_date:
            if self.event_start_time > self.event_end_time:
                raise ValidationError('Start and end times are inconsistent.')


    class Meta:
        ordering = ['category','name']

### Managers below this ###

# EventManager model here...
""" EventManager model class
----------

"""
class EventManager(models.Manager):
    """ EventManager.name_count(keyword)
    -----------
    Returns the number of events that have a name which matches a 
    keyword.

    """
    def name_count(self, keyword):
        return self.filter(name__icontains=keyword).count()

    """ EventManager.search_name_by_keyword(keyword)
    ----------
    Returns a list of elements that have a name which matches a keyword.

    """
    def search_name_by_keyword(self, keyword):
        return self.filter(name__icontains=keyword)
