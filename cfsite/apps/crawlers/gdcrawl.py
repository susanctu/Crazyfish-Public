__author__ = "Georges Goetz"
__email__ = "ggoetz@stanford.edu"
__status__ = "Prototype"

import gspread
from cfsite.apps.events.models import Event, Location, Category
from django.core.exceptions import ValidationError

# TODO: figure out how to securely connect to the spreadsheet
# Username and password in the code is probably a terrible idea...
EVENTS_USERNAME = 'crazyfish.events@gmail.com'
EVENTS_PASSWORD = 'crazyfishPA'
# EVENTS_SPREADSHEET_KEY = '0AokDNrqFh15QdDVJLVZ0V2FyU2FmLWJjaV9rakwyVHc' # Production spreadsheet
EVENTS_SPREADSHEET_KEY = '0AokDNrqFh15QdGJESTFpdVhLbTNsaVd5NjNNVENFNFE'
EVENTS_WORKSHEET_NAME = 'Events'


class GdocsParsingError(Exception):
    """ GdocsParsingError
    ----------
    Custom exception class used for raising errors which happen
    while parsing the Google Docs document.

    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class GdocsCrawler:
    """ GdocsCrawler
    ----------
    A class used to interface and load events from a  Google spreadsheet
    into the crazyfish DB of events.

    """
    events_worksheet = gspread.Worksheet
    events_fields_and_pos = {}
    events_metadata = {}

    def __init__(self):
        """ GdocsCrawler.__init__()
        ----------
        Init method for the GdocsCrawler class.

        """
        self.load_spreadsheet()
        self.build_event_fields_dictionary()
        self.build_metadata_dictionary()

    def load_spreadsheet(self):
        """ GdocsCrawler.load_spreadsheet()
        ----------
        Connects to Google Docs using the class password and
        spreadsheet, and loads the Events spreadsheet from
        the class spreadsheet key.
        If the function fails, it will raise an exception.

        """
        try:
            gc = gspread.login(get_user_name(), get_password())
            sht = gc.open_by_key(get_spreadsheet_key())
            self.events_worksheet = sht.worksheet(get_worksheet_name())
        except gspread.AuthenticationError as e:
            raise GdocsParsingError('Authentication failed: ' + e.__str__())
        except gspread.SpreadsheetNotFound as e:
            raise GdocsParsingError('Spreadsheet not found: ' + e.__str__())
        except gspread.WorksheetNotFound as e:
            raise GdocsParsingError('Worksheet not found: ' + e.__str__())
        except:
            raise GdocsParsingError('Unknown error happened while loading the worksheet')

    def build_event_fields_dictionary(self):
        """ GdocsCrawler.build_event_fields_dictionary()
        ----------
        This function builds the dictionary of events fields from the
        header of the events worksheet. The header is assumed to be
        the first row of the spreadsheet exactly.
        The function will raise an exception

        """
        # Get the worksheet header. Assumed to be the first row.
        header_values = self.events_worksheet.row_values(1)
        # Parsing the worksheet header... Kind of ugly!
        for i in range(0, len(header_values)):
            c_header_name = header_values[i]
            if c_header_name.find('Name') >= 0:
                self.events_fields_and_pos['name'] = i
            elif c_header_name.find('Category') >= 0:
                self.events_fields_and_pos['category'] = i
            elif c_header_name.find('Description') >= 0:
                self.events_fields_and_pos['description'] = i
            elif c_header_name.find('Location') >= 0:
                self.events_fields_and_pos['event_location'] = i
            elif c_header_name.find('Address') >= 0:
                self.events_fields_and_pos['address'] = i
            elif c_header_name.find('Website') >= 0:
                self.events_fields_and_pos['website'] = i
            elif c_header_name.find('Start date') >= 0:
                self.events_fields_and_pos['event_start_date'] = i
            elif c_header_name.find('Start time') >= 0:
                self.events_fields_and_pos['event_start_time'] = i
            elif c_header_name.find('End date') >= 0:
                self.events_fields_and_pos['event_end_date'] = i
            elif c_header_name.find('End time') >= 0:
                self.events_fields_and_pos['event_end_time'] = i
            elif c_header_name.find('Price') >= 0:
                self.events_fields_and_pos['price'] = i
            elif c_header_name.find('Pricing details') >= 0:
                self.events_fields_and_pos['price_details'] = i
            elif c_header_name.find('Rating') >= 0:
                self.events_fields_and_pos['rating'] = i
        # Verifying we've got all the fields required...
        # There should be 13 exactly.
        if len(self.events_fields_and_pos) != 13:
            raise GdocsParsingError('Could not parse the Events worksheet header.')

    def build_metadata_dictionary(self):
        """ GdocsCrawler.build_metadata_dictionary()
        ----------
        This function builds a dictionary which stores where the event metadata
        is located in the spreadsheet (for example, event ID, or flag which
        indicates if event needs to be updated or not).

        """
        header_values = self.events_worksheet.row_values(1)
        for i in range(0, len(header_values)):
            if header_values[i].find("Event ID") >= 0:
                self.events_metadata['event_id'] = i
            if header_values[i].find("Update") >= 0:
                self.events_metadata['update_indicator'] = i

    @property
    def number_of_events(self):
        """ GdocsCrawler.number_of_events()
        ----------
        Returns the number of events found in the worksheet.
        This function assumes that the first row _only_ of the worksheet
        is a header. Anything happening on the second row and below is fair
        game and should be parsed.

        @return: number of events in the Events worksheet.
        @rtype: int

        """
        # All events should have a name, so we can count the number of names
        # and return that as our answer.
        # Note: indices are 1-based in the spreadsheet
        event_names = self.events_worksheet.col_values(
            self.events_fields_and_pos['name']+1)
        return len(event_names)-1

    @property
    def new_events_indices(self):
        """ GdocsCrawler.new_events_indices()
        ----------
        Returns a list of indices (0-based) of all the events that do not have
        a database ID specified in the spreadsheet. These events are assumed to
        correspond to events not yet entered in the database.

        @return: a list of indices for all the events in the spreadsheet that
        do not have IDs
        @rtype: list(int)

        """
        new_events_indices = []
        for i in range(0, self.number_of_events):
            if self.get_id_nth_event(i) < 0:
                new_events_indices.append(i)
        return new_events_indices

    @property
    def updated_events_indices_and_ids(self):
        """ GdocsCrawler.updated_events_indices()
        ----------
        Returns a list of (indices, ids) tuples for all the events in the
        spreadsheet which have been marked as updated.
        Indices are 0-based and correspond to the position of the event in the
        spreadsheet. Ids are the database ID of the updated event.

        @return: a list of (indices, ids tuples) for all the events in the
        spreadsheet that have been entered in the database and since then
        flagged as modified.
        @rtype: list((int, int))

        """
        updated_events_indices_and_ids = []
        for i in range(0, self.number_of_events):
            if self.is_nth_event_updated(i):
                updated_events_indices_and_ids.append(
                    (i, self.get_id_nth_event(i))
                )
        return updated_events_indices_and_ids

    def get_nth_event(self, n):
        """ GdocsCrawler.get_nth_event
        ----------
        Returns an Event object filled with the data entered for the n-th event
        defined in the spreadsheet.
        Raises an exception if the event data could not properly be parsed.

        @param n: index of the element to return (0-based, ie first event after
        the header is event 0 - even if it is on line 2)
        @type n: int

        @return: Event object representing the data entered in the spreadsheet
        @rtype: Event

        """
        # Loading raw input
        event_data = self.events_worksheet.row_values(n+2)

        try:
            # Finding the location
            location_name = event_data[
                self.events_fields_and_pos['event_location']
            ]
            l = Location.objects.get(city=location_name)

            # Creating event object, first with fields that cannot be omitted
            e = Event(name=event_data[self.events_fields_and_pos['name']],
                      event_location=l,
                      website=event_data[
                          self.events_fields_and_pos['website']],
                      event_start_date=event_data[
                          self.events_fields_and_pos['event_start_date']],
                      event_start_time=event_data[
                          self.events_fields_and_pos['event_start_time']],
                      is_valid_event=True)

            # Then, add the optional fields if they have been specified
            if self.events_fields_and_pos['description'] < len(event_data):
                if event_data[self.events_fields_and_pos['description']]:
                    e.description = event_data[
                        self.events_fields_and_pos['description']
                    ]

            if self.events_fields_and_pos['address'] < len(event_data):
                if event_data[self.events_fields_and_pos['address']]:
                    e.address = event_data[
                        self.events_fields_and_pos['address']
                    ]

            if self.events_fields_and_pos['event_end_date'] < len(event_data):
                if event_data[self.events_fields_and_pos['event_end_date']]:
                    e.event_end_date = event_data[
                        self.events_fields_and_pos['event_end_date']
                    ]

            if self.events_fields_and_pos['event_end_time'] < len(event_data):
                if event_data[self.events_fields_and_pos['event_end_time']]:
                    e.event_end_time = event_data[
                        self.events_fields_and_pos['event_end_time']
                    ]

            if self.events_fields_and_pos['price'] < len(event_data):
                if event_data[self.events_fields_and_pos['price']]:
                    e.price = event_data[
                        self.events_fields_and_pos['price']
                    ]

            if self.events_fields_and_pos['price_details'] < len(event_data):
                if event_data[self.events_fields_and_pos['price_details']]:
                    e.price_details = event_data[
                        self.events_fields_and_pos['price_details']
                    ]

            if self.events_fields_and_pos['rating'] < len(event_data):
                if event_data[self.events_fields_and_pos['rating']]:
                    e.rating = event_data[
                        self.events_fields_and_pos['rating']
                    ]

            return e

        except ValidationError as e:
            raise GdocsParsingError('Could not parse line %d of Events worksheet: %s'
                                    % (n+1, e.__str__()))

    def get_categories_nth_element(self, n):
        """ GdocsCrawler.get_categories_nth_element
        ----------
        Returns the list of categories that are associated with the n-th event
        in the document. The Event object has to be build in to step, first it
        needs to be instantiated, and then the list of categories in the
        ManyToMany field should be updated.

        @warning: the function will silently discard unknown categories, and
        if no matching category is found, it will put the event in the "other"
        category.

        @param n: index of the event for which the list of categories is needed.
        Event indexes are 0-based, so the Event on line 2 of the Worksheet is
        the event with index 0.
        @type n: int

        @return: list of Categories
        @rtype: list(Category)

        """
        # Loading raw input
        event_data = self.events_worksheet.row_values(n+2)
        event_categories = event_data[self.events_fields_and_pos['category']]
        event_categories = event_categories.split(",")
        categories_list = []

        # Building the list of categories
        # Warning: the program will silently ignore unknown category names
        for category_name in event_categories:
            try:
                categories_list.append(Category.objects.get(base_name__iexact=category_name.strip()))
            except:
                continue

        if not categories_list:
            categories_list.append(Category.objects.get(base_name__iexact=u'other'))

        return categories_list

    def get_id_nth_event(self, n):
        """ GdocsCrawler.get_id_nth_event(n)
        ----------
        Returns the ID of the n-th event if it exists in the spreadsheet.
        If the ID does not exist (which means the event hasn't been added
        to the database yet) then it return -1.

        @param n: 0-based index of the event for which the ID is queried
        @type n: int

        @return: ID of the event if it is in the spreadsheet (it should then
        correspond to the ID in the database), -1 if no ID.
        @rtype: int

        """
        # Note: cell uses 1-based indexing
        id_data = self.events_worksheet.cell(
            n+2, self.events_metadata['event_id']+1
        ).value
        if id_data:
            return int(id_data)
        else:
            return -1

    def is_nth_event_updated(self, n):
        """ GdocsCrawler.is_nth_event_updated(n)
        ----------
        Returns a boolean indicating if the nth event was flagged as updated
        or not. This method does not check if this event was entered in the
        database (i.e. if the nth event has a database id).

        @param n: 0-based index of the event for which the update status is
        queried
        @type n: int

        @return: True
        @rtype: Boolean

        """
        #Note: cell uses 1-based indexing
        update_data = self.events_worksheet.cell(
            n+2, self.events_metadata['update_indicator']+1
        ).value
        if update_data == "Y" and self.get_id_nth_event(n) < 0:
            return True
        else:
            return False

    def write_id_nth_event(self, n, eid):
        """ GdocsCrawler.write_id_nth_event(n, eid)
        ----------
        Writes the ID of the n-th event in the relevant cell in the gDocs
        worksheet. Returns a boolean indicator of success.

        @param n: 0-based index of the event for which the ID should be updated
        @type n: int

        @param eid: id to be written in the spreadsheet
        @type eid: int

        """
        # Note: cell uses 1-based indexing
        self.events_worksheet.update_cell(
            n+2, self.events_metadata['event_id']+1, str(eid)
        )

    def write_update_status_nth_event(self, n, status):
        """ GdocsCrawler.write_update_status_nth_event(n, status)
        ----------
        Writes the update status of the n-th event in the relevant cell in the
        gDocs worksheet. Returns a boolean indicator of success.

        @param n: 0-based index of the event for which the ID should be updated
        @type n: int

        @param status: if True, then will write "Y" in the cell, otherwise will
        write "N".
        @type status: Boolean

        """
        # Note: cell uses 1-based indexing
        if status:
            self.events_worksheet.update_cell(
                n+2, self.events_metadata['update_indicator']+1, "Y"
            )
        else:
            self.events_worksheet.update_cell(
                n+2, self.events_metadata['update_indicator']+1, "N"
            )


def get_user_name():
    """ getUserName()
    ----------
    Returns the username used to log on to the Google spreadsheet
    containing the events list.

    @rtype: str

    """
    return EVENTS_USERNAME


def get_password():
    """ get_password()
    ----------
    Returns the password corresponding to the username used
    for connecting to the Google spreadsheet.

    @rtype: str

    """
    return EVENTS_PASSWORD


def get_spreadsheet_key():
    """ get_spreadsheet_key()
    ----------
    Returns the Google Docs key to the spreadsheet used for
    loading events.

    @rtype: str

    """
    return EVENTS_SPREADSHEET_KEY


def get_worksheet_name():
    """ get_worksheet_name()
    ----------
    Returns the name of the worksheet which holds the event list
    of interest in the Google Docs spreadsheet.

    @rtype: str

    """
    return EVENTS_WORKSHEET_NAME
