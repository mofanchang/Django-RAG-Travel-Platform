from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )

    def test_profile_redirect_if_not_logged_in(self):
        """未登入應重新導向到登入頁"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_profile_logged_in(self):
        """登入後應能看到個人資料頁"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_shows_email(self):
        """個人資料頁應顯示使用者 email"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertContains(response, 'test@example.com')


class LoginPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )

    def test_login_page_status_200(self):
        """登入頁應回傳 200"""
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_success_redirects(self):
        """登入成功後應重新導向"""
        response = self.client.post('/accounts/login/', {
            'login': 'test@example.com',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_wrong_password(self):
        """密碼錯誤應停留在登入頁"""
        response = self.client.post('/accounts/login/', {
            'login': 'test@example.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)


class SignupPageTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_page_status_200(self):
        """註冊頁應回傳 200"""
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user(self):
        """註冊後應建立新使用者"""
        response = self.client.post('/accounts/signup/', {
            'email': 'newuser@example.com',
            'password1': 'Str0ngPass!',
            'password2': 'Str0ngPass!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_signup_duplicate_email(self):
        """重複的 email 不應能註冊"""
        User.objects.create_user(
            email='existing@example.com',
            password='testpass123',
        )
        response = self.client.post('/accounts/signup/', {
            'email': 'existing@example.com',
            'password1': 'Str0ngPass!',
            'password2': 'Str0ngPass!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='existing@example.com').count(), 1)
