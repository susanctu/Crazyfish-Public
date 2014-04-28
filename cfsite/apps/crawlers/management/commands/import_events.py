# for command and option parsing
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

# for event retrieval and saving
from cfsite.apps.events.models import Event, Location, Category, MAX_DESCRIPTION_LEN, MAX_NAME_LEN
from cfsite.apps.crawlers.deduplication import SimpleDeduplicator
from cfsite.apps.crawlers.management.commands._import_from_feeds \
    import get_and_parse_stanford_general, get_and_parse_stanford_sport, get_and_parse_cityofpaloalto, \
    get_and_parse_paloaltoplayers
from cfsite.apps.crawlers.management.commands._import_from_ebrite import get_and_parse_eventbrite_JSON
from cfsite.apps.crawlers.management.commands._import_from_meetup import get_and_parse_meetup_JSON
from cfsite.apps.crawlers.management.commands._errors import SourceRetrievalError
from django.db.utils import DataError

class Command(BaseCommand):
    """
    Defines the behavior of and options accepted by
    python manage.py import_events.

    Since this command could be called from call_command, in
    which case we might want to redirect the output, nothing
    in this class or the helper methods that it calls should
    call print. All output should be directed to self.stdout
    or self.stderr.
    """
    help = 'Pulls events from various apis and feeds and adds to database'

    SOURCE_TYPES = ['api', 'feed']
    API_SOURCES = ['ebrite','meetup']
    FEED_SOURCES = ['stanford-general', 'stanford-sport', 'cityofpaloalto', 'paloaltoplayers']
    SOURCES = API_SOURCES + FEED_SOURCES
    SOURCE_TO_GEN = dict(zip(SOURCES, [
        get_and_parse_eventbrite_JSON,
        get_and_parse_meetup_JSON,
        get_and_parse_stanford_general,
        get_and_parse_stanford_sport,
        get_and_parse_cityofpaloalto,
        get_and_parse_paloaltoplayers]))

    option_list = BaseCommand.option_list + (
        make_option('--source_type',
            action='store',
            type='string',
            help='What type of sources to pull from. '
                 'Either \'apis\' or \'feeds\''),
        make_option('--sources',
            action='store',
            type='string',
            help='Which sources to pull from. '
                 'Choices are %s' % (' '.join(FEED_SOURCES)),
            )
        )

    def handle(self, *args, **options):
        source_list = options.get('sources')
        source_type = options.get('source_type')
        source_generators = self.SOURCES # default to all sources
        if source_list and source_type:
            raise SourceRetrievalError("Cannot simultaneously specify both sources and source_type")
        elif source_list:
            source_list = self._validate_and_parse_into_list(source_list)
            source_generators = source_list
        elif source_type:
            if source_type == "apis":
                source_generators = self.API_SOURCES
            elif source_type == "feeds":
                source_generators = self.FEED_SOURCES
            else:
                raise SourceRetrievalError("Unrecognized source_type: %s" % source_type)

        self._import_events(self._get_sources_generators(source_generators))

    def _get_sources_generators(self, sources_str_list):
        """
        Takes a list of strings specifying the sources.
        Returns a list of generators that yield data from those sources.
        """
        return [self.SOURCE_TO_GEN[source_str]() for source_str in sources_str_list]

    def _validate_and_parse_into_list(self,sources_str):
        """
        Takes a comma, separated list of sources, checks that each listed
        source is a valid source to pull from, returns list of source
        names that can be passed to _get_sources_generators
        """
        sources_list = sources_str.split(",")
        for source in sources_list:
            if not source in self.SOURCES:
                raise SourceRetrievalError("Unrecognized source: %s" % source)
        return sources_list 

    def _save_event_model(self, event_list):
        """
        Save each of the events (represented as dicts)
        in event_list.
        """
        self.stdout.write('Saving events to database:')
        for event_dict in event_list:
            ev = Event(
                name=event_dict['name'][:MAX_NAME_LEN],
                event_location=Location.objects.get_or_create(
                    city='Palo Alto',
                    state_province='CA',
                    zip_code=94303,
                    country='United States',
                    timezone='US/Pacific',
                    )[0], # discard second element (a bool) of tuple
                event_start_date=event_dict['start_datetime'].date(),
                event_start_time=event_dict['start_datetime'].time(),
                is_valid_event=True)

            if 'end_datetime' in event_dict:
                ev.event_end_date = event_dict['end_datetime'].date()
                ev.event_end_time = event_dict['end_datetime'].time()
            if 'price' in event_dict:
                ev.price = event_dict['price']
            if 'url' in event_dict:
                ev.website = event_dict['url']
            if 'description' in event_dict:
                if len(event_dict['description']) > MAX_DESCRIPTION_LEN:
                    ev.description = 'Please visit event website for the event description.'
                else:
                    ev.description = event_dict['description'][:MAX_DESCRIPTION_LEN]
                self.stdout.write('Description len: %s' % len(ev.description))
            if 'address' in event_dict:
                ev.address = event_dict['address']

            if (SimpleDeduplicator.is_duplicate(ev)):
                self.stdout.write('Skipping duplicate...')
            else:
                self.stdout.write(event_dict['name'])
                try: 
                    ev.save()
                    for category in event_dict['categories']:
                        cat, unused_is_new_bool = Category.objects.get_or_create(base_name=category)
                        ev.category.add(cat)
                except DataError:
                    pass # could not save event, probably some field is too long for our db. skip

    def _import_events(self, sources_generators):
        for gen in sources_generators:
            try:
                while True:
                    self._save_event_model(next(gen))
            except StopIteration:
                self.stdout.write('...Finished pulling from one data source') # TODO (susanctu): in future, maybe we want to print some stats


