from django.contrib import admin
from events.models import Event, Location, Category

class LocationAdmin(admin.ModelAdmin):
    list_display = ('city','zip_code','state_province','country',)
    ordering = ('zip_code',)
    search_fields = ('city','zip_code',)

class EventAdmin(admin.ModelAdmin):
    list_display = ('name','event_start_date','event_start_time',
                    'event_end_time','event_location','price','website',)
    list_filter = ('category','event_start_date',)
    ordering = ('category','-event_start_date',)
    search_fields = ('category','event_start_date','location',)

# Register the models here.
admin.site.register(Category)
admin.site.register(Location, LocationAdmin)
admin.site.register(Event, EventAdmin)
