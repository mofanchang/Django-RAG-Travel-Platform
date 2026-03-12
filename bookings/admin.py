from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total', 'status', 'paypal_transaction_id')
    search_fields = ('user__email',)
    list_filter = ('status',)
