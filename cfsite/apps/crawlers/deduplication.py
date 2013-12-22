__author__ = 'Georges Goetz'
__email__ = "ggoetz@stanford.edu"
__status__ = "Prototype"

from cfsite.apps.events.models import Event


class SimpleDeduplicator:
    """ SimpleDeduplicator
    ----------
    SimpleDeduplicator does simple de-duplication by looking for exact
    matches for events in the event database.

    """

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
        @type event__and_md_list: list((Event, event_metadata))

        @return: a list of events which have not been found already
        in the database
        @rtype: list(Event)
        """
        return filter(lambda (x, y): SimpleDeduplicator.is_not_duplicate(x), event_and_md_list)

    @staticmethod
    def is_not_duplicate(event):
        """ SimpleDeduplicator.is_not_duplicate(event)
        ----------
        Returns true if the event is not detected as a duplicate of any other
        event in the database, and false otherwise.

        @param event: a (Event, event_metadata) tuple.

        @return: Boolean,
        """
        #TODO
        # Simple de duplication starts by looking for events that happen on
        # the same date, and have the same categorization.

        # Filter out events whose start time is too different (outside a +/-
        # 1 hour time window.

        # Then, look for events whose name matches the name of the new event
        # (= string edit distance within n, n TBD)

        # If name, categories, start date match and start time is very close,
        # then we very probably have a duplicate here. Flag it as such!
        return False