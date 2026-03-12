from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from trips.models import Trip
from datetime import date, timedelta

User = get_user_model()

TODAY = date.today()
FUTURE_START = TODAY + timedelta(days=30)
FUTURE_END = TODAY + timedelta(days=35)


class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.trip = Trip.objects.create(
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

    def test_cart_view_status_200(self):
        """購物車頁面應回傳 200"""
        response = self.client.get(reverse('cart_view'))
        self.assertEqual(response.status_code, 200)

    def test_add_to_cart(self):
        """加入購物車後應重新導向"""
        response = self.client.get(reverse('add_to_cart', args=[self.trip.id]))
        self.assertEqual(response.status_code, 302)

    def test_add_to_cart_stores_in_session(self):
        """加入購物車後 session 應包含該行程 ID"""
        self.client.get(reverse('add_to_cart', args=[self.trip.id]))
        cart = self.client.session.get('cart', [])
        self.assertIn(self.trip.id, cart)

    def test_add_same_trip_twice_no_duplicate(self):
        """同一行程加入兩次不應重複"""
        self.client.get(reverse('add_to_cart', args=[self.trip.id]))
        self.client.get(reverse('add_to_cart', args=[self.trip.id]))
        cart = self.client.session.get('cart', [])
        self.assertEqual(cart.count(self.trip.id), 1)

    def test_remove_from_cart(self):
        """移除購物車後 session 不應包含該行程"""
        self.client.get(reverse('add_to_cart', args=[self.trip.id]))
        self.client.get(reverse('remove_from_cart', args=[self.trip.id]))
        cart = self.client.session.get('cart', [])
        self.assertNotIn(self.trip.id, cart)

    def test_clear_cart(self):
        """清空購物車後 session 應為空"""
        self.client.get(reverse('add_to_cart', args=[self.trip.id]))
        self.client.get(reverse('clear_cart'))
        cart = self.client.session.get('cart', [])
        self.assertEqual(len(cart), 0)
