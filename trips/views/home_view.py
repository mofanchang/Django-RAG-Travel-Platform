from django.shortcuts import render
from trips.models import Trip
import random

def home_view(request):
    all_trips = list(Trip.objects.all())
    popular_trips = random.sample(all_trips, min(len(all_trips), 6))
    context = {'trips': popular_trips}
    return render(request, 'home.html', context)

