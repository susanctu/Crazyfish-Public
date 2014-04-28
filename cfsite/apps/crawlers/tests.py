from django.test import TestCase
from cfsite.apps.crawlers.deduplication import SimpleDeduplicator
from cfsite.apps.events.models import Location, Category, Event
from datetime import datetime
 
class OneEventInDbDeduplicationTestCase(TestCase):
    def setUp(self):
        """Populate database with only one event"""
        self.create_fake_event()

    def test_remove_one_duplicate(self):
        """
        remove_duplicated_from_event_list identifies
        that a single event is a duplicate
        TODO (susanctu): fix before adding too many other tests:
        if too much time passes between setup and running of
        this test, this test will fail because the fake event's time
        is the time of creation
        """
        orig_list=[(self.create_fake_event(),'dummy metadata')]
        filtered_lst = SimpleDeduplicator.remove_duplicates_from_event_list(orig_list)
        self.assert_(not filtered_lst)

    def create_fake_event(self):
        """Returns a dummy event."""
        # TODO (susanctu): should code like (i.e., that creates fakes/mocks/stubs for classes) this belong somewhere else?
        ev = Event(
            name='dummy event',
            event_location=Location.objects.get_or_create(
                city='Palo Alto',
                state_province='CA',
                zip_code=94301,
                country='US',
                timezone='Pacific',
                )[0],
            website='www.crazyfish.com',
            event_start_date=datetime.now().today(),
            event_start_time=datetime.now().time(),
            is_valid_event=True)
        cat = Category.objects.get_or_create()[0];
        ev.save()
        ev.category.add(cat);
        return ev

    def test_not_a_duplicate(self):
        """ 
        remove_duplicate_from_event_list does not identify
        nonduplicate as duplicate 
        """
        # TODO (susanctu): finish this
        # ev = Event();
        # ev.save();
        # SimpleDeduplicator.remove_duplicates_from_event_list(
        #    [(ev,'dummy metadata')])


