import gspread
from cfsite.apps.events.models import Event, Location, Category
from django.core.exceptions import ValidationError

# TODO: figure out how to securely connect to the spreadsheet
# Username and password in the code is probably a terrible idea...
EVENTS_USERNAME = 'crazyfish.events@gmail.com'
EVENTS_PASSWORD = 'crazyfishPA'
EVENTS_SPREADSHEET_KEY = '0AokDNrqFh15QdDVJLVZ0V2FyU2FmLWJjaV9rakwyVHc'
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

    def __init__(self):
        """ GdocsCrawler.__init__()
        ----------
        Init method for the GdocsCrawler class.

        """
        self.load_spreadsheet()
        self.build_event_fields_dictionary()

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
        num_fields = len(header_values)
        # Parsing the worksheet header... Kind of ugly!
        # Note that column indices are 1-based and not 0-based, hence the frequent +1.
        for i in range(0, num_fields-1):
            c_header_name = header_values[i]
            if c_header_name.find('Name'):
                self.events_fields_and_pos['name'] = i+1
            elif c_header_name.find('Category'):
                self.events_fields_and_pos['category'] = i+1
            elif c_header_name.find('Description'):
                self.events_fields_and_pos['description'] = i+1
            elif c_header_name.find('Location'):
                self.events_fields_and_pos['event_location'] = i+1
            elif c_header_name.find('Address'):
                self.events_fields_and_pos['address'] = i+1
            elif c_header_name.find('Website'):
                self.events_fields_and_pos['website'] = i+1
            elif c_header_name.find('Start date'):
                self.events_fields_and_pos['event_start_date'] = i+1
            elif c_header_name.find('Start time'):
                self.events_fields_and_pos['event_start_time'] = i+1
            elif c_header_name.find('End date'):
                self.events_fields_and_pos['event_end_date'] = i+1
            elif c_header_name.find('End time'):
                self.events_fields_and_pos['event_end_time'] = i+1
            elif c_header_name.find('Price'):
                self.events_fields_and_pos['price'] = i+1
            elif c_header_name.find('Pricing details'):
                self.events_fields_and_pos['price_details'] = i+1
            elif c_header_name.find('Rating'):
                self.events_fields_and_pos['rating'] = i+1
        # Verifying we've got all the fields required... There should be 13 exactly.
        if len(self.events_fields_and_pos) != 13:
            raise GdocsParsingError('Could not parse the Events worksheet header.')

    def get_number_of_events(self):
        """ GdocsCrawler.get_number_of_events
        ----------
        Returns the number of events found in the worksheet.
        This function assumes that the first row _only_ of the worksheet
        is a header. Anything happening on the second row and below is fair game
        and should be parsed.

        @return: number of events in the Events worksheet.
        @rtype: int
        """
        # All events should have a name, so we can count the number of names and return
        # that as our answer.
        event_names = self.events_worksheet.col_values(self.events_fields_and_pos['name'])
        return len(event_names)-1

    def get_nth_event(self, n):
        """ GdocsCrawler.get_nth_event
        ----------
        Returns an Event object filled with the data entered for the n-th event
        defined in the spreadsheet.
        Raises an exception if the event data could not properly be parsed.

        @param n: index of the element to return (0-based, ie first event after the header
        is event 0 - even if it is on line 2)
        @type n: int

        @return: Event object representing the data entered in the spreadsheet
        @rtype: Event
        """
        # Loading raw input
        event_data = self.events_worksheet.row_values(n+2)

        try:
            # Finding the location
            location_name = event_data[self.events_fields_and_pos['event_location']]
            l = Location.objects.get(city=location_name)

            # Creating event object, first with fields that cannot be omitted
            e = Event(name=event_data[self.events_fields_and_pos['name']],
                      event_location=l,
                      website=event_data[self.events_fields_and_pos['website']],
                      event_start_date=event_data[self.events_fields_and_pos['event_start_date']],
                      event_start_time=event_data[self.events_fields_and_pos['event_start_time']],
                      is_valid_event=True)

            # Then, add the optional fields if they have been specified
            if event_data[self.events_fields_and_pos['description']]:
                e.description = event_data[self.events_fields_and_pos['description']]
            if event_data[self.events_fields_and_pos['address']]:
                e.address = event_data[self.events_fields_and_pos['address']]
            if event_data[self.events_fields_and_pos['event_end_time']]:
                e.event_end_date = event_data[self.events_fields_and_pos['event_end_date']]
            if event_data[self.events_fields_and_pos['event_end_time']]:
                e.event_end_time = event_data[self.events_fields_and_pos['event_end_time']]
            if event_data[self.events_fields_and_pos['price']]:
                e.price = event_data[self.events_fields_and_pos['price']]
            if event_data[self.events_fields_and_pos['price_details']]:
                e.price_details = event_data[self.events_fields_and_pos['price_details']]
            if event_data[self.events_fields_and_pos['rating']]:
                e.rating = event_data[self.events_fields_and_pos['rating']]

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
        @rtype: Category
        """
        # Loading raw input
        event_data = self.events_worksheet.row_values(n+2)
        event_categories = event_data(self.events_fields_and_pos['category'])
        event_categories = event_categories.split(",")
        categories_list = []

        # Building the list of categories
        # Warning: the program will silently ignore unknown category names
        for category_name in event_categories:
            try:
                categories_list.append(Category.objects.get(base_name=category_name.strip()))
            except:
                continue

        if not categories_list:
            categories_list.append(Category.objects.get(base_name=u'other'))

        return categories_list


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
