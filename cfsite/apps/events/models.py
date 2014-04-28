__author__ = "Georges Goetz"
__email__ = "ggoetz@stanford.edu"
__status__ = "Prototype"

import datetime
from django.db import models
from django.core.exceptions import ValidationError

# the crazyfish categories
ART = 'arts & culture'
CLASS = 'classes & workshop'
CONF = 'conference'
FAM = 'family'
SPORT = 'sport'
MUSIC = 'music'
MEET = 'meetup'
FOOD = 'food & wine'

CF_CATEGORIES = [ART, CLASS, CONF, FAM, MUSIC, MEET, FOOD, SPORT]

MAX_DESCRIPTION_LEN = 10000
MAX_NAME_LEN = 100

### Models for the event app here ###

# Location model here
class Location(models.Model):
    """ Location model class
    ----------
    This class represents a pre-approved location where events take place.
    The location has the following fields:
        - city: name of the city where events take place
        - zip_code: zip code of the city
        - state_province: optional, used only if the event takes place in the US
        or in Canada
        - country: country where the events take place.
        - timezone: local time zone.

    Each event in the database is tied to one instance of the Location class,
    so that events are always linked to a known location. Events which cannot be
    linked to a known event will need to be approved manually, after the
    location where the event takes place has been verified.

    """
    city = models.CharField(max_length=60)
    state_province = models.CharField('state or province', max_length=30,
                                      blank=True)
    country = models.CharField(max_length=50)
    zip_code = models.PositiveIntegerField('zip code', max_length=5)
    timezone = models.CharField(max_length=50)

    def __unicode__(self):
        """ Location.__unicode__
        ----------
        Defines the formatting of a Location

        """
        return self.city

    def clean(self):
        """ Location.clean()
        ----------
        Custom validation method, which runs the following checks:
            - if state_or_province is stripped if country is not "U.S.A."
            or "Canada"
            - if country is USA or Canada, then the state_or_province should be
            provided

        """
        # Don't allow events happening in CA or USA to not have a state or
        # province
        if self.country == 'United States' or self.country == 'Canada':
            if not self.state_province:
                raise ValidationError(
                    'Events in the USA or Canada must have a state or province')
        # For events outside these two countries, strip the state or province.
        else:
            self.state_province = ""

    class Meta:
        ordering = ['zip_code']


# Category model here...
class Category(models.Model):
    """ Category model class
    ----------
    This class represents a category for an event. Categories can consist only
    of     a generic classification (stored in base_name), or they can also have
    a sub-category type of classification (stored in sub_category).

    In general, an event will be tied only to one category, but it is possible
    to associate an event with multiple categories as well.

    """
    base_name = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        """ Category.__unicode__
        ----------
        Formatting of a category

        """
        if self.sub_category:
            return u'%s/%s' % (self.base_name, self.sub_category)
        else:
            return u'%s/all' % self.base_name

    def clean(self):
        """ Category.clean()
        ----------
        Category validation method.

        """
        pass

    class Meta:
        ordering = ['base_name']
        verbose_name_plural = 'categories'


# EventManager class here
class EventManager(models.Manager):
    """ EventManager model class
    ----------
    This manager provides search functionality in the events database.

    """

    def name_count(self, keyword):
        """ EventManager.name_count(keyword)
        -----------
        Returns the number of events that have a name which matches a
        keyword.

        @type keyword: str
        @param keyword: keyword for which we will search against in
        the database of events.

        """
        return self.filter(name__icontains=keyword).count()

    def search_name_by_keyword(self, keyword):
        """ EventManager.search_name_by_keyword(keyword)
        ----------
        Returns a list of elements that have a name which matches a keyword.

        @type keyword: str
        @param keyword: keyword for which we will do a search against in the
        events database.

        """
        return self.filter(name__icontains=keyword)

    @staticmethod
    def search_for_events(date, location_id):
        """ EventManager.search_for_events(date, location_id)
        ----------
        Returns the list of all events that occurs on the date specified,
        for the matching category and location.
        It assumes that the date requested is specified in the event local
        time zone, and therefore does not make any checks as far as time
        zones go before filtering by date.

        Note: for now, it does not return events which last more than one day
        and do not start on the date specified.

        @type: location_id: int
        @param: location_id: numerical ID of the location of interest

        """
        locations = Location.objects.get(id=location_id)
        l = locations.event_set.filter(event_start_date=date)
        return l


# Event model here...
class Event(models.Model):
    """ Event model class
    ----------
    This class represents a model for the event stored in the database.
    An event is primarily comprised of a name and category. It also needs a
    time and place for it to be valid.
    Optionally, an event can have a price, a description and a website.

    An event can have a different start date from its end date (required for
    events which last more than a day, for example a music festival).
    When the end date and time of and event are not specified, the event is
    assumed to end an hour after its initial start time. If an event end date
    is specified but not the event end hour, the event will be assumed to end
    at midnight on this day.

    Detailed explanation of the fields of this class:
        - name: string summarising the event.
        - category: one (or more) of the previously approved categories for
        events. Note: it is important to use a many-to-many field for this,
        because of the way categories are described. Since there is one Category
        object instance for each category/subcategory combination, it is very
        likely that an event will be linked to more than one Category object,
        even if in the end it only appears in one basic category.
        - description: string describing the event, optional.
        - event_location: one of the previously approved locations for events.
        - address: string giving the address of the event (street and number),
        optional. The location (city, country) should not be present in this
        string, because it is already included in the event_location field.
        - website: website where tickets can be bought.
        - event_start_date: start date of the event.
        - event_end_date: optional, end time of the event.
        - event_start_time: start time of the event.
        - event_end_time: optional, end time of the event. If it is not
        specified and the event end date was specified, then the event is
        assumed to end at 23:59 on the day of the event end.
        - price: optional, typical price of the event (starting price).
        - price_details: optional, string describing in more details the pricing
        policy for the event.
        - rating: list of integer ratings, between 0 and 5.
        - is_valid_event: flag, used to choose if events should be served to the
        user or not.

    """

    name = models.CharField(max_length=MAX_NAME_LEN)
    category = models.ManyToManyField(Category)
    description = models.CharField(max_length=MAX_DESCRIPTION_LEN, blank=True)
    event_location = models.ForeignKey(Location)
    address = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    event_start_date = models.DateField('start date')
    event_end_date = models.DateField('end date, optional',
                                      blank=True, null=True)
    event_start_time = models.TimeField('start time')
    event_end_time = models.TimeField('end time', blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    price_details = models.CharField(max_length=200, blank=True)
    rating = models.CommaSeparatedIntegerField(max_length=250, blank=True)
    is_valid_event = models.BooleanField('Is event valid?')
    objects = EventManager()

    def __unicode__(self):
        """ Event.__unicode__
        ----------
        Defines the formatting of an event

        """
        return self.name

    def clean(self):
        """ Event.clean()
        ----------
        Custom model validation, which runs the following sanity checks:
            - price should be always be positive
            - event start time should be before event end time.
            - an event should always be linked to the generic 'All/generic'
            category.

        """
        # Price should always be positive
        if self.price < 0:
            raise ValidationError('Price cannot be negative')

        # Plug in default values if end date and end time weren't specified
        # If the end date was specified, the end time could be implied.
        if self.event_end_date is not None and self.event_end_time is None:
            self.event_end_time.hours = datetime.time(23, 59, 0)
        if self.event_end_date is None:
            self.event_end_date = self.event_start_date

        # If event duration was not specified, set start time to end time
        # to indicate we don't know what to do with the time.
        if self.event_end_time is None:
            self.event_end_time = self.event_start_time

        # Check that start and end date and time of the event are consistent
        if self.event_end_date < self.event_start_date:
            raise ValidationError('Start and end dates are inconsistent.')
        elif self.event_end_date == self.event_start_date:
            if self.event_start_time > self.event_end_time:
                raise ValidationError('Start and end times are inconsistent.')

    def category_names(self):
        """ Category.category_names()
        ----------
        Database query used to display event category.

        """
        return', '.join([a.__unicode__ for a in self.category.all()])
    category_names.short_description = "Categories"

    def compare(self, new_obj):
        """ Event.compare(new_obj)
        ----------
        Compares the event object with another event object.
        Returns a dictionary with the changed attributes between self and
        new_obj. Values of the attributes are those of new_obj.

        @param new_obj: new event.
        @type new_obj: Event

        @return: dictionary of changed attributes

        """
        ignore_keys = 'created', '_state', 'timestamp', 'user', 'uid', 'changed'
        return Event._compare(self, new_obj, ignore_keys)

    @staticmethod
    def _compare(old_obj, new_obj, ignore_keys):
        """ Event._compare(old_obj, new_obj, ignore_keys)
        ----------
        Compares two Event objects (an old one and a new one) and returns
        a dictionary of attributes which differ between the two. The values
        associated with the key are those of the new object.
        @warning: will silently ignore fields present in one object which are
        not present in the other.

        @param old_obj: older Event
        @type old_obj: Event

        @param new_obj: newer Event
        @type new_obj: Event

        @param ignore_keys: dictionary of keys to ignore when comparing Events
        @type ignore_keys: dict

        @return: dictionary of attributes which differ between old and new

        """
        d_old, d_new = old_obj.__dict__, new_obj.__dict__
        change = {}
        for k, v in d_old.items():
            if k in ignore_keys:
                continue
            try:
                if v != d_new[k]:
                    change.update({k: d_new[k]})
            except KeyError:
                continue

        return change

    class Meta:
        ordering = ['event_start_time', 'name']

