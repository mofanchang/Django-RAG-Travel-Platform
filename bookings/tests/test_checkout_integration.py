"""
整合測試：購物車 → 結帳 → 建立訂單 → 庫存扣減
測試範圍：完整的 HTTP request/response 流程，包含資料庫操作
"""
from django.test import TestCase, Client
from django.contrib.messages import get_messages
from accounts.models import CustomUser
from trips.models import Trip
from cart.models import Cart, CartItem
from bookings.models import Booking, BookingItem
from decimal import Decimal
import datetime


class CartIntegrationTest(TestCase):
    """購物車功能整合測試"""

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.trip = Trip.objects.create(
            name='測試東京行程',
            description='五天四夜',
            price=Decimal('25000.00'),
            start_date=datetime.date(2026, 6, 1),
            end_date=datetime.date(2026, 6, 5),
            available_seats=10,
            location='日本',
            duration=5,
            country='日本',
            city='東京',
        )

    def test_add_to_cart_requires_login(self):
        """未登入不能加購物車，應重新導向登入頁"""
        res = self.client.get(f'/cart/add_to_cart/{self.trip.id}/')
        self.assertRedirects(res, f'/accounts/login/?next=/cart/add_to_cart/{self.trip.id}/')

    def test_add_to_cart_creates_db_record(self):
        """登入後加入購物車，應在資料庫建立 CartItem"""
        self.client.login(email='test@example.com', password='testpass123')
        self.client.get(f'/cart/add_to_cart/{self.trip.id}/')

        cart = Cart.objects.get(user=self.user)
        self.assertTrue(CartItem.objects.filter(cart=cart, trip=self.trip).exists())

    def test_add_to_cart_no_duplicate(self):
        """同一行程加兩次，CartItem 應只有一筆"""
        self.client.login(email='test@example.com', password='testpass123')
        self.client.get(f'/cart/add_to_cart/{self.trip.id}/')
        self.client.get(f'/cart/add_to_cart/{self.trip.id}/')

        cart = Cart.objects.get(user=self.user)
        self.assertEqual(CartItem.objects.filter(cart=cart, trip=self.trip).count(), 1)

    def test_remove_from_cart(self):
        """移除行程後 CartItem 應消失"""
        self.client.login(email='test@example.com', password='testpass123')
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, trip=self.trip)

        self.client.post(f'/cart/remove_from_cart/{self.trip.id}/')
        self.assertFalse(CartItem.objects.filter(cart=cart, trip=self.trip).exists())


class CheckoutIntegrationTest(TestCase):
    """結帳與訂單整合測試"""

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            email='buyer@example.com',
            password='testpass123',
        )
        self.trip = Trip.objects.create(
            name='測試峇里島行程',
            description='七天六夜',
            price=Decimal('38000.00'),
            start_date=datetime.date(2026, 7, 1),
            end_date=datetime.date(2026, 7, 7),
            available_seats=5,
            location='印尼',
            duration=7,
            country='印尼',
            city='峇里島',
        )
        self.client.login(email='buyer@example.com', password='testpass123')
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, trip=self.trip)

    def test_full_checkout_creates_booking(self):
        """完整結帳流程：POST /bookings/create/ 應建立 Booking 和 BookingItem"""
        res = self.client.post('/bookings/create/')

        self.assertEqual(Booking.objects.filter(user=self.user).count(), 1)
        booking = Booking.objects.get(user=self.user)
        self.assertEqual(BookingItem.objects.filter(booking=booking).count(), 1)
        self.assertEqual(booking.total, Decimal('38000.00'))

    def test_checkout_decrements_available_seats(self):
        """結帳後行程的 available_seats 應減少"""
        self.client.post('/bookings/create/')

        self.trip.refresh_from_db()
        self.assertEqual(self.trip.available_seats, 4)  # 5 - 1 = 4

    def test_checkout_clears_cart(self):
        """結帳成功後購物車應被清空"""
        self.client.post('/bookings/create/')

        cart = Cart.objects.get(user=self.user)
        self.assertEqual(CartItem.objects.filter(cart=cart).count(), 0)

    def test_checkout_via_get_is_blocked(self):
        """GET 請求不能建立訂單，應重新導向購物車"""
        res = self.client.get('/bookings/create/')
        self.assertRedirects(res, '/cart/cart/')
        self.assertEqual(Booking.objects.count(), 0)


class OversellProtectionTest(TestCase):
    """高併發防超賣整合測試"""

    def setUp(self):
        self.trip = Trip.objects.create(
            name='限量衝浪行程',
            description='只剩最後一席',
            price=Decimal('15000.00'),
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2026, 8, 3),
            available_seats=1,  # 只剩 1 席
            location='台灣',
            duration=3,
            country='台灣',
            city='墾丁',
        )

    def _make_user_with_cart(self, email):
        user = CustomUser.objects.create_user(email=email, password='testpass123')
        cart, _ = Cart.objects.get_or_create(user=user)
        CartItem.objects.create(cart=cart, trip=self.trip)
        return user

    def test_only_one_booking_succeeds_when_one_seat_left(self):
        """
        當只剩 1 席時，兩位用戶同時結帳，只有一筆訂單應該成功。
        另一筆應收到座位不足的錯誤訊息。
        """
        user1 = self._make_user_with_cart('user1@example.com')
        user2 = self._make_user_with_cart('user2@example.com')

        client1 = Client()
        client2 = Client()
        client1.login(email='user1@example.com', password='testpass123')
        client2.login(email='user2@example.com', password='testpass123')

        # 模擬先後結帳（真正的高併發測試需用 threading，此處測邏輯正確性）
        client1.post('/bookings/create/')
        res2 = client2.post('/bookings/create/')

        # 只應有 1 筆訂單成功
        self.assertEqual(Booking.objects.count(), 1)
        # available_seats 不應變成負數
        self.trip.refresh_from_db()
        self.assertGreaterEqual(self.trip.available_seats, 0)

        # User2 應收到錯誤訊息
        storage = get_messages(res2.wsgi_request)
        messages = [str(m) for m in storage]
        self.assertTrue(any('座位' in m for m in messages))
