from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Trip(models.Model):
    """旅遊行程模型"""
    
    # 基本資訊
    name = models.CharField(max_length=200, verbose_name='行程名稱')
    description = models.TextField(verbose_name='行程描述')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='價格'
    )
    image = models.ImageField(
        upload_to='trips/', 
        max_length=500, 
        blank=True, 
        null=True,
        verbose_name='行程圖片'
    )
    
    # 日期資訊
    start_date = models.DateField(verbose_name='開始日期')
    end_date = models.DateField(verbose_name='結束日期')
    available_seats = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='可用座位數'
    )
    
    # 地點資訊
    location = models.CharField(max_length=100, verbose_name='地點')
    country = models.CharField(max_length=100, verbose_name='國家')
    city = models.CharField(max_length=100, verbose_name='城市')
    
    # 行程屬性
    duration = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='行程天數'
    )
    keywords = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name='關鍵字',
        help_text='用於搜尋和推薦的關鍵字，以逗號分隔'
    )
    
    # 狀態管理
    is_active = models.BooleanField(
        default=True,
        verbose_name='啟用狀態',
        help_text='未啟用的行程不會顯示在前台'
    )
    featured = models.BooleanField(
        default=False,
        verbose_name='精選行程',
        help_text='精選行程會優先顯示'
    )
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        ordering = ['-featured', '-created_at']
        verbose_name = '旅遊行程'
        verbose_name_plural = '旅遊行程'
        indexes = [
            models.Index(fields=['country', 'city']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active', '-featured']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return self.name
    
    @property
    def is_available(self):
        """檢查行程是否可預訂"""
        return (
            self.is_active and 
            self.available_seats > 0 and 
            self.start_date >= timezone.now().date()
        )
    
    @property
    def days_until_start(self):
        """距離出發還有幾天"""
        if self.start_date < timezone.now().date():
            return 0
        return (self.start_date - timezone.now().date()).days
    
    def get_booking_count(self):
        """獲取已預訂數量"""
        from bookings.models import BookingItem
        return BookingItem.objects.filter(trip=self).count()
