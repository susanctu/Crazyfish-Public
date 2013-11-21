from django.contrib import admin
from events.model import Event, Location, Category

class LocationAdmin(admin.ModelAdmin):
    list_display('city','zip_code','state_province','country')
    ordering('zip-code')
    search_fields('city','zip_code')

class EventAdmin(admin.ModelAdmin):
    list_display('name','category','event_date','event_start_time',
                 'event_end_time','location','price','website')
    list_filter('category','event_date')
    ordering = ('category','-event_date')
    search_fields = ('category','event_date','location')

# Register the models here.
admin.register(Category)
admin.register(Location, LocationAdmin)
admin.site.register(Event, EventAdmin)
