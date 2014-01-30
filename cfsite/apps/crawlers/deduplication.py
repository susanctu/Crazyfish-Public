__author__ = 'Georges Goetz'
__email__ = "ggoetz@stanford.edu"
__status__ = "Prototype"

import datetime
from cfsite.apps.events.models import Event

class SimpleDeduplicator:
    """ SimpleDeduplicator
    ----------
    SimpleDeduplicator does simple de-duplication by looking for exact
    matches for events in the event database.

    """
    DAY_TIME_START = datetime.time(0,0,0)
    DAY_TIME_END = datetime.time(23,59,0)

    def __init__(self):
        """ SimpleDeduplicator.__init__()
        ----------
        __init__() does nothing.

        """

    @staticmethod
    def remove_duplicates_from_event_list(event_and_md_list):
        """ SimpleDeduplicator.remove_duplicates_from_event_list
        ----------
        This function cleans up a list of events and removes the duplicates
        that it finds using the SimpleDeduplicator duplication detection
        heuristics.
        Note: it does not check for pairs of duplicates *inside* the list!

        @param event_and_md_list: a list of events from which duplicates should
        be removed. The list has the event object and associated metadata.
        @type event_and_md_list: list((Event, event_metadata))

        @return: a list of events which have not been found already
        in the database
        @rtype: list(Event)
        """
        return filter(lambda (x, y): not(SimpleDeduplicator.is_duplicate(x)), event_and_md_list)

    @staticmethod
    def is_duplicate(event):
        """ SimpleDeduplicator.is_duplicate(event)
        ----------
        Returns true if the event is detected as a duplicate of another
        event in the database, and false otherwise.

        @param event: a (Event, event_metadata) tuple.

        @return: Boolean, True is the event is detected in the database,
        False otherwise.

        """
        # Parameters we'll filter against
        e_date = event.event_start_date
        e_time = event.event_start_time
        e_name = event.name.strip()
        time_window = datetime.timedelta(minutes=30)
        e_datetime = datetime.datetime.combine(e_date, e_time)

        # Simple de duplication starts by looking for events that happen on
        # the same date, inside a +/- 30 minutes time window, with at least
        # one matching category.
        # Also looks for events whose name matches the name of the new event

        if e_datetime < \
           datetime.datetime.combine(e_date, SimpleDeduplicator.DAY_TIME_START) + time_window: 
            time_window_start = SimpleDeduplicator.DAY_TIME_START
        else: 
            time_window_start = (e_datetime - time_window).time()

        if e_datetime > \
           datetime.datetime.combine(e_date, SimpleDeduplicator.DAY_TIME_END) - time_window:
            time_window_end = SimpleDeduplicator.DAY_TIME_END
        else: 
            time_window_end = (e_datetime + time_window).time()

        matching_events_queryset = Event.objects.filter(
            name__icontains=e_name
        ).filter(
            event_start_date__exact=e_date
        ).exclude(
            event_start_time__lt=time_window_start
        ).exclude(
            event_start_time__gt=time_window_end
        )

        # If name, start date match and start time is very close,
        # then we very probably have a duplicate here. Flag it as such!
        if matching_events_queryset.all():
            return True
        else:
            return False
