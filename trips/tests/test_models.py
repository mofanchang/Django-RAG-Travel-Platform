from django.test import TestCase
from trips.models import Trip
from datetime import date, timedelta

# 動態日期，永遠是未來
TODAY = date.today()
FUTURE_START = TODAY + timedelta(days=30)
FUTURE_END = TODAY + timedelta(days=35)


class TripModelTest(TestCase):
    def setUp(self):
        self.trip = Trip.objects.create(
            name="東京美食探索五日遊",
            description="探索東京必訪景點，品嚐道地日本美食",
            price=18900.00,
            image="tokyo.jpg",
            start_date=FUTURE_START,
            end_date=FUTURE_END,
            available_seats=20,
            location="東京",
            duration=5,
            country="日本",
            city="東京",
            keywords="東京,美食,購物,文化"
        )

    def test_trip_creation(self):
        """Trip 物件應該能成功建立"""
        self.assertIsInstance(self.trip, Trip)

    def test_trip_str(self):
        """Trip __str__ 應回傳行程名稱"""
        self.assertEqual(str(self.trip), "東京美食探索五日遊")

    def test_trip_fields(self):
        """Trip 欄位值應正確儲存"""
        self.assertEqual(self.trip.city, "東京")
        self.assertEqual(self.trip.country, "日本")
        self.assertEqual(self.trip.duration, 5)
        self.assertEqual(self.trip.available_seats, 20)

    def test_trip_price(self):
        """Trip 價格應正確儲存"""
        self.assertEqual(float(self.trip.price), 18900.00)

    def test_trip_dates(self):
        """Trip 日期應正確儲存"""
        self.assertEqual(self.trip.start_date, FUTURE_START)
        self.assertEqual(self.trip.end_date, FUTURE_END)
