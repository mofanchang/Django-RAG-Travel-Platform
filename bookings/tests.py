from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from trips.models import Trip
from bookings.models import Booking, BookingItem
from datetime import date, timedelta

User = get_user_model()

TODAY = date.today()
FUTURE_START = TODAY + timedelta(days=30)
FUTURE_END = TODAY + timedelta(days=35)


class BookingListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
        self.booking = Booking.objects.create(
            user=self.user,
            total=18900.00,
            status='Pending'
        )

    def test_booking_list_redirect_if_not_logged_in(self):
        """未登入應重新導向到登入頁"""
        response = self.client.get(reverse('bookings:booking_list'))
        self.assertEqual(response.status_code, 302)

    def test_booking_list_logged_in(self):
        """登入後應能看到訂單列表"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('bookings:booking_list'))
        self.assertEqual(response.status_code, 200)

    def test_booking_list_shows_own_bookings(self):
        """訂單列表應只顯示自己的訂單"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('bookings:booking_list'))
        self.assertContains(response, str(self.booking.id))


class BookingDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            username='otheruser'
        )
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
        self.booking = Booking.objects.create(
            user=self.user,
            total=18900.00,
            status='Pending'
        )
        BookingItem.objects.create(
            booking=self.booking,
            trip=self.trip,
            quantity=1,
            unit_price=self.trip.price
        )

    def test_booking_detail_logged_in(self):
        """登入後應能看到訂單詳情"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('bookings:booking_detail', args=[self.booking.id]))
        self.assertEqual(response.status_code, 200)

    def test_booking_detail_shows_trip(self):
        """訂單詳情頁應顯示行程名稱"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('bookings:booking_detail', args=[self.booking.id]))
        self.assertContains(response, '東京經典五日遊')

    def test_booking_detail_other_user_cannot_view(self):
        """其他使用者不能查看別人的訂單"""
        self.client.login(email='other@example.com', password='testpass123')
        response = self.client.get(reverse('bookings:booking_detail', args=[self.booking.id]))
        self.assertEqual(response.status_code, 404)


class CheckoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
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

    def test_checkout_redirect_if_not_logged_in(self):
        """未登入應重新導向到登入頁"""
        response = self.client.get(reverse('bookings:checkout'))
        self.assertEqual(response.status_code, 302)

    def test_checkout_logged_in(self):
        """登入後應能進入結帳頁"""
        self.client.login(email='test@example.com', password='testpass123')
        session = self.client.session
        session['cart'] = [self.trip.id]
        session.save()
        response = self.client.get(reverse('bookings:checkout'))
        self.assertEqual(response.status_code, 200)

    def test_checkout_shows_correct_total(self):
        """結帳頁應顯示正確金額"""
        self.client.login(email='test@example.com', password='testpass123')
        session = self.client.session
        session['cart'] = [self.trip.id]
        session.save()
        response = self.client.get(reverse('bookings:checkout'))
        self.assertContains(response, '18900.00')


class CreateBookingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
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

    def test_create_booking_redirect_if_not_logged_in(self):
        """未登入應重新導向到登入頁"""
        response = self.client.get(reverse('bookings:create_booking'))
        self.assertEqual(response.status_code, 302)

    def test_create_booking_empty_cart_redirects(self):
        """購物車為空時建立訂單應重新導向"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('bookings:create_booking'))
        self.assertEqual(response.status_code, 302)

    def test_create_booking_success(self):
        """有購物車內容時應成功建立訂單"""
        self.client.login(email='test@example.com', password='testpass123')
        session = self.client.session
        session['cart'] = [self.trip.id]
        session.save()
        response = self.client.get(reverse('bookings:create_booking'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Booking.objects.filter(user=self.user).count(), 1)

    def test_create_booking_creates_booking_items(self):
        """建立訂單後應同時建立 BookingItem"""
        self.client.login(email='test@example.com', password='testpass123')
        session = self.client.session
        session['cart'] = [self.trip.id]
        session.save()
        self.client.get(reverse('bookings:create_booking'))
        booking = Booking.objects.get(user=self.user)
        self.assertEqual(booking.items.count(), 1)
        self.assertEqual(booking.items.first().trip, self.trip)

    def test_create_booking_clears_cart(self):
        """建立訂單後購物車應被清空"""
        self.client.login(email='test@example.com', password='testpass123')
        session = self.client.session
        session['cart'] = [self.trip.id]
        session.save()
        self.client.get(reverse('bookings:create_booking'))
        cart = self.client.session.get('cart', [])
        self.assertEqual(len(cart), 0)
