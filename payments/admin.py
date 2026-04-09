from django.contrib import admin
from .models import PremiumTransaction


@admin.register(PremiumTransaction)
class PremiumTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'listing', 'amount', 'status', 'payment_method', 'created_at')
    list_display_links = ('id',)
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__email', 'listing__title', 'transaction_id', 'sberbank_order_id')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Информация о транзакции', {
            'fields': ('user', 'listing', 'amount', 'currency', 'payment_method')
        }),
        ('Статус', {
            'fields': ('status', 'transaction_id', 'sberbank_order_id', 'created_at', 'updated_at', 'completed_at')
        }),
        ('Описание', {
            'fields': ('description',)
        }),
    )
