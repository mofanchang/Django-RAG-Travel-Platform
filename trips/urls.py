# trips/urls.py

from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('', views.trip_list, name='trip_list'),
    path('search/', views.trip_search, name='trip_search'),  #  確保這個存在
    path('<int:pk>/', views.trip_detail, name='trip_detail'),
]





