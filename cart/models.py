from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from trips.models import Trip

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.quantity > 10:
            self.quantity = 10
        super().save(*args, **kwargs)