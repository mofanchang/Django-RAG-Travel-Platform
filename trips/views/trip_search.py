import requests
import logging
from django.shortcuts import render
from django.conf import settings
from trips.models import Trip
from decouple import config

logger = logging.getLogger(__name__)

def trip_search(request):
    trips = Trip.objects.all()
    query = request.POST.get('destination', '').strip() if request.method == "POST" else request.GET.get('destination', '').strip()
    start_date = request.POST.get('start_date') if request.method == "POST" else request.GET.get('start_date')
    end_date = request.POST.get('end_date') if request.method == "POST" else request.GET.get('end_date')

    if query:
        # 嘗試使用 RAG 語義搜尋
        try:
            rag_url = f"http://{config('DB_HOST', default='localhost')}:{config('RAG_PORT', default='8000')}/search"
            response = requests.post(rag_url, json={"query": query, "topK": 20}, timeout=5)
            if response.status_code == 200:
                results = response.json().get('results', [])
                trip_ids = [r['id'] for r in results]
                # 保持語義排序
                preserved_order = {id: pos for pos, id in enumerate(trip_ids)}
                semantic_trips = list(Trip.objects.filter(id__in=trip_ids))
                semantic_trips.sort(key=lambda x: preserved_order.get(x.id, 999))
                trips = Trip.objects.filter(id__in=trip_ids) # 接著進行日期過濾
            else:
                logger.warning(f"RAG server returned error: {response.status_code}")
                trips = trips.filter(city__icontains=query)
        except Exception as e:
            logger.error(f"Failed to connect to RAG server: {e}")
            # 發生錯誤時回退到傳統搜尋
            trips = trips.filter(city__icontains=query)

    if start_date:
        trips = trips.filter(start_date__gte=start_date)
    if end_date:
        trips = trips.filter(end_date__lte=end_date)

    if request.method == "POST" or query:
        return render(request, 'trips/trip_search_results.html', {'trips': trips, 'query': query})

    return render(request, 'home.html')
