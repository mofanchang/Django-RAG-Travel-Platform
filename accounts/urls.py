# filepath: accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    # 你可以再加其他帳號相關功能
    # path('edit/', views.edit_profile, name='edit_profile'),
]