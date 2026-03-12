from django.test import TestCase, Client
from unittest.mock import patch
from trips.models import Trip
import json


class RAGRecommendTest(TestCase):
    def setUp(self):
        Trip.objects.create(
            name="東京三日遊",
            description="東京經典行程，包含淺草寺、新宿、原宿",
            price=10000,
            image="tokyo.jpg",
            start_date="2025-07-01",
            end_date="2025-07-03",
            available_seats=10,
            location="東京",
            duration=3,
            country="日本",
            city="東京",
            keywords="東京,城市,購物,美食",
        )

    def test_recommend_returns_result(self):
        """RAG 推薦應該回傳至少一個結果"""
        from chatbot.services.service import recommend_trips_with_rag
        results = recommend_trips_with_rag("我想去東京", single_result=True)
        self.assertGreater(len(results), 0)

    def test_recommend_fallback_when_no_rag(self):
        """RAG 沒有初始化時，應該 fallback 回傳熱門產品"""
        from chatbot.llm import rag_instance
        # 清空向量資料，模擬未初始化狀態
        rag_instance.trip_embeddings = None
        rag_instance.trips_data = None

        from chatbot.services.service import recommend_trips_with_rag
        results = recommend_trips_with_rag("隨便推薦", single_result=True)
        self.assertGreater(len(results), 0)


class ChatAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        Trip.objects.create(
            name="首爾五日遊",
            description="首爾美食與文化探索",
            price=15000,
            image="seoul.jpg",
            start_date="2025-08-01",
            end_date="2025-08-05",
            available_seats=8,
            location="首爾",
            duration=5,
            country="韓國",
            city="首爾",
            keywords="首爾,美食,文化,購物",
        )

    def test_chat_api_post(self):
        """聊天 API 應該回傳 200 和推薦結果"""
        response = self.client.post(
            '/chatbot/chat/',
            data=json.dumps({"message": "我想去韓國"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("recommended_trips", data)
        self.assertIn("reply", data)

    def test_chat_api_empty_message(self):
        """空訊息應該回傳 400"""
        response = self.client.post(
            '/chatbot/chat/',
            data=json.dumps({"message": ""}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_chat_api_get_not_allowed(self):
        """GET 方法應該回傳 405"""
        response = self.client.get('/chatbot/chat/')
        self.assertEqual(response.status_code, 405)
