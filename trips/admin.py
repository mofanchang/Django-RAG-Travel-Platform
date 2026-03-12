from django.contrib import admin
from .models import Trip

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'start_date', 'end_date', 'available_seats')
    search_fields = ('name',)
    list_filter = ('start_date', 'end_date')

