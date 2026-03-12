from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from trips.models import Trip
from cart.models import Cart, CartItem


@login_required
def add_to_cart(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    CartItem.objects.get_or_create(cart=cart, trip=trip)
    return redirect('cart_view')


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.select_related('trip').all()
    total = sum(item.trip.price for item in items)
    return render(request, 'cart/cart.html', {'items': items, 'total': total})


@login_required
def remove_from_cart(request, trip_id):
    if request.method == 'POST':
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            CartItem.objects.filter(cart=cart, trip_id=trip_id).delete()
    return redirect('cart_view')


@login_required
def clear_cart(request):
    if request.method == 'POST':
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.cartitem_set.all().delete()
    return redirect('cart_view')
