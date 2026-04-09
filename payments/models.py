from django.db import models
from django.conf import settings
from listings.models import Listing


class PremiumTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('completed', 'Успешно'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возврат'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('sberbank', 'Сбербанк'),
        ('card', 'Банковская карта'),
        ('mock', 'Тестовый режим'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='premium_transactions')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='premium_transactions', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='mock')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    sberbank_order_id = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Премиум транзакция'
        verbose_name_plural = 'Премиум транзакции'
        ordering = ['-created_at']

    def __str__(self):
        return f"Транзакция {self.id} - {self.user.email} - {self.amount} {self.currency}"

    def mark_as_completed(self, transaction_id=None):
        from django.utils.timezone import now
        self.status = 'completed'
        self.completed_at = now()
        if transaction_id:
            self.transaction_id = transaction_id
        self.save(update_fields=['status', 'completed_at', 'transaction_id'])

        if self.listing:
            from datetime import timedelta
            self.listing.is_premium = True
            self.listing.premium_until = now() + timedelta(days=7)
            self.listing.save(update_fields=['is_premium', 'premium_until'])

    def mark_as_failed(self):
        self.status = 'failed'
        self.save(update_fields=['status'])

    def mark_as_refunded(self):
        self.status = 'refunded'
        self.save(update_fields=['status'])
