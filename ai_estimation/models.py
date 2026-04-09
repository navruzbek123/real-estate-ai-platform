from django.db import models
from django.conf import settings


class AIEstimationHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_estimations')
    area = models.IntegerField(help_text='Площадь в м²')
    rooms = models.IntegerField()
    city = models.CharField(max_length=100)
    floor = models.IntegerField()
    total_floors = models.IntegerField(default=5)
    property_type = models.CharField(max_length=50, default='apartment')
    home_type = models.CharField(max_length=50, default='Condo')
    estimated_price = models.IntegerField()
    confidence = models.FloatField(default=0.85)
    is_premium_user = models.BooleanField(default=False)
    discount_applied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'История AI оценки'
        verbose_name_plural = 'Истории AI оценок'
        ordering = ['-created_at']

    def __str__(self):
        return f"AI Оценка - {self.user.email} - {self.area}м² - {self.created_at.strftime('%d.%m.%Y')}"
