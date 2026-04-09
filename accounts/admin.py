from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserAccount, Notification, UserProfile


@admin.register(UserAccount)
class UserAccountAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_display_links = ('id', 'name')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('name', 'email', 'phone')
    list_per_page = 25

    fieldsets = (
        ('Основная информация', {
            'fields': ('email', 'name', 'password', 'role')
        }),
        ('Контакт', {
            'fields': ('phone', 'avatar', 'bio')
        }),
        ('AI Оценки', {
            'fields': ('ai_estimations_today', 'ai_estimations_this_month', 'last_ai_estimation_date')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'role', 'is_staff'),
        }),
    )

    ordering = ('-date_joined',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notification_type', 'title', 'is_read', 'created_at')
    list_display_links = ('id',)
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'dark_mode', 'notifications_enabled', 'email_notifications', 'created_at')
    list_display_links = ('id', 'user')
    list_filter = ('dark_mode', 'notifications_enabled', 'email_notifications')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
