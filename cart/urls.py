from django.urls import path
from .views import add_to_cart, cart_view,remove_from_cart,clear_cart
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('add_to_cart/<int:trip_id>/', add_to_cart, name='add_to_cart'),  # 加入購物車
    path('cart/', cart_view, name='cart_view'),# 購物車內容
    path('remove_from_cart/<int:trip_id>/', remove_from_cart, name='remove_from_cart'),
    path('clear/', clear_cart, name='clear_cart'),
    
]


