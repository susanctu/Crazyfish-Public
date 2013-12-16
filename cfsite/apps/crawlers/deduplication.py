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
    def remove_duplicates_from_event_list(event_list):
        """ SimpleDeduplicator.remove_duplicates_from_event_list
        ----------
        This function cleans up a list of events and removes the duplicates
        that it finds using the SimpleDeduplicator duplication detection
        heuristics.

        @param event_list: a list of events from which duplicates should
        be removed. The list has the event object and associated metadata.
        @type event_list: list((Event, event_metadata))

        @return: a list of events which have not been found already
        in the database
        @rtype: list(Event)
        """
        #TODO
        #TODO: duplication is naturally done using filter() (FP approach)
        #TODO: figure out how to remove possible duplicate pairs in this list, without adding them to DB?
        return event_list

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
        return False