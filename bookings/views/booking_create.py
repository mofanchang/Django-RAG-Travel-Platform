from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from bookings.models import Booking, BookingItem
from cart.models import Cart
from trips.models import Trip
from decimal import Decimal


class InsufficientSeatsError(Exception):
    """行程座位不足時拋出"""
    def __init__(self, trip_name):
        self.trip_name = trip_name


@login_required
def create_booking(request):
    if request.method != 'POST':
        return redirect('cart_view')

    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('cart_view')

    items = list(cart.cartitem_set.select_related('trip').all())
    if not items:
        return redirect('cart_view')

    try:
        booking = _process_booking(request.user, items)
        cart.cartitem_set.all().delete()
        return redirect('bookings:booking_detail', booking_id=booking.id)

    except InsufficientSeatsError as e:
        messages.error(request, f'「{e.trip_name}」的座位已不足，請移除後再結帳。')
        return redirect('bookings:checkout')


def _process_booking(user, items):
    """
    在 transaction 內加鎖處理訂單，防止高併發超賣。
    使用 select_for_update() 鎖定 Trip 資料列，直到 transaction 結束。
    """
    with transaction.atomic():
        total = Decimal('0')
        locked_trips = []

        for item in items:
            # 用 select_for_update() 加悲觀鎖，其他同時進行的 transaction 必須等待
            trip = Trip.objects.select_for_update().get(id=item.trip.id)

            if trip.available_seats < item.quantity:
                raise InsufficientSeatsError(trip.name)

            trip.available_seats -= item.quantity
            trip.save()

            total += trip.price * item.quantity
            locked_trips.append((trip, item.quantity))

        # 建立訂單
        booking = Booking.objects.create(
            user=user,
            total=total,
            status='Pending'
        )

        # 建立訂單明細（記錄當下價格，日後改價不影響歷史訂單）
        for trip, quantity in locked_trips:
            BookingItem.objects.create(
                booking=booking,
                trip=trip,
                quantity=quantity,
                unit_price=trip.price
            )

        return booking
