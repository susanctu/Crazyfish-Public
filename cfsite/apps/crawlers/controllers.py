__author__ = "Georges Goetz"
__email__ = "ggoetz@stanford.edu"
__status__ = "Prototype"

from cfsite.apps.crawlers.gdcrawl import GdocsCrawler
from cfsite.apps.events.models import Event, Category
from cfsite.apps.crawlers.deduplication import SimpleDeduplicator


class GdocsCrawlerController:
    """ GdocsCrawlerController
    ----------
    A controller for the GdocsCrawler.
    It takes care of validating the events that the GdocsCrawler returns,
    adds them to the database if they are valid and not duplicates of
    events already parsed.

    """
    gdc = GdocsCrawler
    _event_list = []
    _event_index_list = []

    def __init__(self):
        """ GdocsCrawlerController.__init__()
        ----------
        __init__() creates an instance of a GdocsCrawler, which will then be
        controlled through the methods of the GdocsCrawlerController.
        The event list is not loaded, because it is slow and it should only
        happen at the user's request.

        """
        self.gdc = GdocsCrawler()

    @property
    def event_list(self):
        """ GdocsCrawlerController.event_list
        ----------
        Get the current event list.

        @return: a list of Events that are all new (ie don't have an ID yet)
        @rtype: Event
        """
        return self._event_list

    def load_event_list(self):
        """ GdocsCrawlerController.load_event_list
        ----------
        Returns a list of all the new events that the GdocsCrawler found in the
        GoogleDocs spreadsheet. These events have not been checked for
        duplication at this point, they are detected as new only from the data
        entered in the spreadsheet. No database queries happen here.

        """
        self._event_index_list = self.gdc.new_events_indices()
        self._event_list = []
        for i in self._event_index_list:
            c_event = self.gdc.get_nth_event(i)
            c_cat_list = self.gdc.get_categories_nth_element(i)
            for cat in c_cat_list:
                assert isinstance(cat, Category)
                c_event.category.add(cat)
            self._event_list.append(c_event)

    def cleanup_event_list(self):
        """ GdocsCrawlerController.cleanup_event_list()
        ----------
        Calls one of the deduplicators event list cleanup method in order to
        remove duplicates from a list of event which was stored in
        self.event_list.
        This is a dangerous method to use for deduplication, as duplication
        inside the list will not be accounted for. It is fine to call it if
        you can guarantee there are no duplicate events within the list.

        """
        self._event_list, self._event_index_list = \
            zip(*SimpleDeduplicator.remove_duplicates_from_event_list(
                zip(self._event_list, self._event_index_list)))

    def add_events_to_database(self):
        """ GdocsCrawlerController.add_events_to_database()
        ----------
        Adds the list of events in self._event_list to the database of events.
        For each event added, it writes in the GoogleDocs spreadsheet the DB ID
        of the event.

        @return: True on success, False on fail.
        @rtype: Boolean
        """
        #TODO
        return False