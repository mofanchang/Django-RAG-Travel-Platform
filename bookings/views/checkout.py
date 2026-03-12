from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart


@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.select_related('trip').all()
    total = sum(item.trip.price for item in items)
    return render(request, 'bookings/checkout.html', {
        'items': items,
        'total': total
    })
