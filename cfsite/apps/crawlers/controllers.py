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
    _event_id_list = []

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

    def load_new_events_list(self):
        """ GdocsCrawlerController.load_new_events_list
        ----------
        Loads the list of all the new events that the GdocsCrawler found in the
        GoogleDocs spreadsheet. These events have not been checked for
        duplication at this point, they are detected as new only from the data
        entered in the spreadsheet. No database queries happen here.
        The event list is loaded in the _event_list field of the object, and
        corresponding event ids are loaded in _event_index_list.

        """
        self._event_index_list = self.gdc.new_events_indices
        self.populate_event_list_from_index_list()

    def load_updated_events_list(self):
        """ GdocsCrawlerController.load_updated_events_list
        ----------
        Loads the list of all the events that were flagged as updated in the
        GoogleDocs spreadsheet.
        The event list is loaded in the _event_list field of the object, and
        the corresponding event ids are loaded in _event_index_list.

        """
        self._event_index_list, self._event_id_list = \
            zip(*self.gdc.updated_events_indices_and_ids)
        self.populate_event_list_from_index_list()

    def populate_event_list_from_index_list(self):
        """ GdocsCrawlerController.populate_event_list_from_index_list
        ----------
        Loads the list of events whose ids are stored in _event_index_list
        into the _event_list field.
        This method will erase all events previously present in the _event_list
        in order to make sure indices between _event_index_list and _event_list
        are in sync.

        """
        self._event_list = []
        for i in self._event_index_list:
            c_event = self.gdc.get_nth_event(i)
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
        This method does not call load_new_event_list itself, so the list of
        events should have been populated prior to calling
        add_events_to_database.

        """
        # Adding events sequentially deals with the case where duplicate
        # events exist inside the _event_list field.
        for i in range(0, len(self._event_index_list), 1):
            e = self._event_list[i]
            e_ind = self._event_index_list[i]
            if not(SimpleDeduplicator.is_duplicate(e)):
                e.save()
                self.gdc.write_id_nth_event(e_ind, e.id)
                self._event_id_list.append(e.id)
            # Add categories whether it is a duplicate or not.
            # ManyToMany relationships work like sets, so there won't be a
            # problem with categories appearing more than once if added twice.
            c_cat_list = self.gdc.get_categories_nth_element(e_ind)
            for cat in c_cat_list:
                assert isinstance(cat, Category)
                e.category.add(cat)

    def update_events_in_database(self):
        """ GdocsCrawlerController.update_events_in_database()
        ----------
        Updates all the events whose database ID is stored in _event_id_list
        and replaces them by the events defined in the corresponding line
        of the GoogleDocs spreadsheet.
        This method does not call load_updated_event_list itself, so the user
        should make sure to force this update of the list of events himself,
        before calling update_events_in_database.

        """
        for i in range(0, len(self._event_id_list), 1):
            e_id = self._event_id_list[i]       # DB ID
            e_ind = self._event_index_list[i]   # Index of the event
            e_db = Event.objects.get(id=e_id)   # Event as stored in the DB
            e_db = e_db[0]                      # list to Event object
            e_new = self._event_list[i]         # new Event object

            # Compare the old and the new event, detect which fields have
            # changed and update them in the old.
            change = e_db.compare(e_new)
            for (name, val) in change:
                setattr(e_db, name, val)

            # Save the updated old event, saving of only the fields which
            # have changed
            e_db.save(update_fields=[name for (name, val) in change])

            # Mark the event status as not requiring an update anymore
            self.gdc.write_update_status_nth_event(e_ind, False)