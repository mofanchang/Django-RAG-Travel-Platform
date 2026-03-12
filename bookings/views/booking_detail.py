
from django.shortcuts import render, get_object_or_404
from bookings.models import Booking
from django.contrib.auth.decorators import login_required

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})
