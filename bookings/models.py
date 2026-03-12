from django.db import models
from django.conf import settings
from trips.models import Trip


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')
    paypal_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id} by {self.user.email}"


class BookingItem(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # 記錄當下價格，避免日後改價影響歷史訂單

    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.trip.name} x{self.quantity}"
