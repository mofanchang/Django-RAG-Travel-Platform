from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email 為必填欄位')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

# ─── Google Login 自動連通處理 ────────────────────────────────
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        在社群登入完成前執行，若系統已有相同 Email 的帳號則自動關聯，
        避免「社群網路登入失敗」的跳轉迴圈。
        """
        # 已是存在的社群帳號，直接放行
        if sociallogin.is_existing:
            return

        # 從 Google 回傳資料取得 email
        try:
            email = sociallogin.account.extra_data.get('email')
            if not email and sociallogin.email_addresses:
                email = sociallogin.email_addresses[0].email
        except Exception:
            return

        if not email:
            return

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            # 將 Google 帳號連結到現有使用者
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            # 帳號不存在，讓 allauth 自動建立新帳號
            pass
        except Exception:
            # 發生其他錯誤時靜默略過，讓 allauth 繼續處理
            pass
