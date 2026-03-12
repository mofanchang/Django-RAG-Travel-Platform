from django.contrib import admin
from django.urls import path, include
from trips.views.home_view import home_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('user/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('trips/', include('trips.urls', namespace='trips')),
    path('chatbot/', include('chatbot.urls')),
    path('', home_view, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
