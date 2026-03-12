from django.urls import path
from .views.booking_list import booking_list
from .views.booking_detail import booking_detail
from .views.booking_create import create_booking
from .views.checkout import checkout_view

app_name = 'bookings' 

urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
    path('', booking_list, name='booking_list'),
    path('<int:booking_id>/', booking_detail, name='booking_detail'),
    path('create/', create_booking, name='create_booking'),
]
