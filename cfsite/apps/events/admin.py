__author__ = "Georges Goetz"
__email__ = "ggoetz@stanford.edu"
__status__ = "Prototype"

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from cfsite.apps.events.models import Event, Location, Category


class LocationAdmin(admin.ModelAdmin):
    """ LocationAdmin
    ----------
    Basic administrative model for Locations in the admin panel.

    """
    list_display = ('city', 'zip_code', 'state_province', 'country', 'timezone')
    ordering = ('zip_code', )
    search_fields = ('city', 'zip_code', )


class CategoryAdmin(admin.ModelAdmin):
    """ CategoryAdmin
    ----------
    Basic administrative model for categories in the admin panel.

    """
    list_display = ('base_name', 'sub_category')
    ordering = ('base_name',)
    search_fields = ('base_name',)


class CategoryFilter(SimpleListFilter):
    """ CategoryFilter
    ----------
    Custom filter list for displaying the different events
    filtered by category type.

    """
    # Title displayed in the right admin sidebar
    title = 'category' 
    # Parameter for filter used in URL query
    parameter_name = 'category' 

    def lookups(self, request, model_admin):
        """
        CategoryFilter.lookups(request, model_admin)
        ----------
        Returns a list of tuples, in which the first element is the coded 
        value for the option that will appear in the URL query. The second
        element is the human-readable name for the option that will appear
        in the right sidebar.

        @type request: HttpRequest
        @type model_admin: ModelAdmin

        """
        categories = set([c for c in Category.objects.all()])
        return [(c.id, c.__unicode__) for c in categories]

    def queryset(self, request, queryset):
        """ 
        CategoryFilter.queryset(request, queryset)
        ----------
        Returns the filtered queryset based on the value provided in the 
        query string and retrievable via 'self.value()'.

        @type request: HttpRequest
        @type queryset: queryset

        @rtype: queryset
        """
        if self.value():
            return queryset.filter(category__id__exact=self.value())
        else:
            return queryset


class EventAdmin(admin.ModelAdmin):
    """ EventAdmin
    ----------
    Basic administrative model for Events in the admin panel.

    """
    list_display = ('name', 'category_names', 'event_start_date',
                    'event_start_time', 'event_end_time', 'event_location',
                    'price', 'website', 'is_valid_event')
    list_filter = (CategoryFilter, 'event_start_date', 'event_location')
    ordering = ('-event_start_date',)
    search_fields = ('category', 'event_start_date', 'location',)


# Register the models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Event, EventAdmin)
