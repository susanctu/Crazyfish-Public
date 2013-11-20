from django.contrib import admin
from events.model import Event

class EventAdmin(admin.ModelAdmin):
    list_display('name','category','event_date','event_start_time',
                 'event_end_time','price','website')
    list_filter('category','event_date')
    ordering = ('category','-event_date')
    search_fields = ('category','event_date','city')

# Register the models here.
admin.site.register(Event, EventAdmin)
