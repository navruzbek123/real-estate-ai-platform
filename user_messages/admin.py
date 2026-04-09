from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'subject', 'is_read', 'created_at')
    list_display_links = ('id',)
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__email', 'recipient__email', 'subject', 'body')
    readonly_fields = ('created_at', 'read_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Отправитель и получатель', {
            'fields': ('sender', 'recipient', 'listing')
        }),
        ('Содержание', {
            'fields': ('subject', 'body')
        }),
        ('Статус', {
            'fields': ('is_read', 'read_at', 'created_at')
        }),
    )
