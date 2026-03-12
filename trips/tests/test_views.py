from django.test import TestCase, Client
from django.urls import reverse
from trips.models import Trip
from datetime import date, timedelta

TODAY = date.today()
FUTURE_START = TODAY + timedelta(days=30)
FUTURE_END = TODAY + timedelta(days=35)
FAR_FUTURE_START = TODAY + timedelta(days=60)
FAR_FUTURE_END = TODAY + timedelta(days=65)


class TripListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.trip1 = Trip.objects.create(
            name="東京經典五日遊",
            description="探索東京必訪景點",
            price=18900.00,
            image="tokyo.jpg",
            start_date=FUTURE_START,
            end_date=FUTURE_END,
            available_seats=20,
            location="東京",
            duration=5,
            country="日本",
            city="東京",
            keywords="東京,城市,購物"
        )
        self.trip2 = Trip.objects.create(
            name="首爾韓流五日遊",
            description="體驗首爾韓流文化",
            price=16900.00,
            image="gwanghwamun-636115_640.jpg",
            start_date=FAR_FUTURE_START,
            end_date=FAR_FUTURE_END,
            available_seats=25,
            location="首爾",
            duration=5,
            country="韓國",
            city="首爾",
            keywords="首爾,購物,韓流"
        )

    def test_trip_list_status_200(self):
        """行程列表頁應回傳 200"""
        response = self.client.get(reverse('trips:trip_list'))
        self.assertEqual(response.status_code, 200)

    def test_trip_list_shows_all_trips(self):
        """行程列表頁應顯示所有行程"""
        response = self.client.get(reverse('trips:trip_list'))
        self.assertContains(response, "東京經典五日遊")
        self.assertContains(response, "首爾韓流五日遊")


class TripDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.trip = Trip.objects.create(
            name="沖繩海島度假五日遊",
            description="享受沖繩湛藍海水與南國風情",
            price=22900.00,
            image="okinawa-3421799_640.jpg",
            start_date=FUTURE_START,
            end_date=FUTURE_END,
            available_seats=18,
            location="沖繩",
            duration=5,
            country="日本",
            city="沖繩",
            keywords="沖繩,海島,度假"
        )

    def test_trip_detail_status_200(self):
        """行程詳細頁應回傳 200"""
        response = self.client.get(reverse('trips:trip_detail', args=[self.trip.pk]))
        self.assertEqual(response.status_code, 200)

    def test_trip_detail_shows_correct_trip(self):
        """行程詳細頁應顯示正確的行程資料"""
        response = self.client.get(reverse('trips:trip_detail', args=[self.trip.pk]))
        self.assertContains(response, "沖繩海島度假五日遊")

    def test_trip_detail_404(self):
        """不存在的行程應回傳 404"""
        response = self.client.get(reverse('trips:trip_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)


class TripSearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.trip1 = Trip.objects.create(
            name="東京經典五日遊",
            description="探索東京必訪景點",
            price=18900.00,
            image="tokyo.jpg",
            start_date=FUTURE_START,
            end_date=FUTURE_END,
            available_seats=20,
            location="東京",
            duration=5,
            country="日本",
            city="東京",
            keywords="東京,城市,購物"
        )
        self.trip2 = Trip.objects.create(
            name="首爾韓流五日遊",
            description="體驗首爾韓流文化",
            price=16900.00,
            image="gwanghwamun-636115_640.jpg",
            start_date=FAR_FUTURE_START,
            end_date=FAR_FUTURE_END,
            available_seats=25,
            location="首爾",
            duration=5,
            country="韓國",
            city="首爾",
            keywords="首爾,購物,韓流"
        )

    def test_search_fallback_by_city(self):
        """RAG 不可用時應 fallback 用城市名稱搜尋"""
        response = self.client.post(reverse('trips:trip_search'), {'destination': '東京'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "東京經典五日遊")
        self.assertNotContains(response, "首爾韓流五日遊")

    def test_search_date_filter(self):
        """日期過濾應正確篩選行程"""
        response = self.client.post(reverse('trips:trip_search'), {
            'start_date': FUTURE_START.strftime('%Y-%m-%d'),
            'end_date': FUTURE_END.strftime('%Y-%m-%d'),
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "東京經典五日遊")
        self.assertNotContains(response, "首爾韓流五日遊")

    def test_search_empty_query_returns_home(self):
        """空搜尋 GET 請求應回傳首頁"""
        response = self.client.get(reverse('trips:trip_search'))
        self.assertEqual(response.status_code, 200)
