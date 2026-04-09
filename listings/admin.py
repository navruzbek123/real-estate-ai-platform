from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'realtor', 'city', 'price', 'is_published', 'is_premium', 'status', 'list_date')
    list_display_links = ('id', 'title')
    list_filter = ('realtor', 'is_published', 'is_premium', 'status', 'sale_type', 'home_type', 'list_date')
    list_editable = ('is_published', 'is_premium')
    search_fields = ('title', 'description', 'address', 'city', 'state', 'zipcode', 'price')
    list_per_page = 25
    readonly_fields = ('list_date', 'expiry_date')
    date_hierarchy = 'list_date'

    fieldsets = (
        ('Основная информация', {
            'fields': ('realtor', 'user', 'title', 'slug')
        }),
        ('Местоположение', {
            'fields': ('address', 'city', 'state', 'zipcode')
        }),
        ('Описание', {
            'fields': ('description',)
        }),
        ('Детали', {
            'fields': ('sale_type', 'price', 'bedrooms', 'bathrooms', 'home_type', 'sqft')
        }),
        ('Фото', {
            'fields': ('photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 'photo_5')
        }),
        ('Статус', {
            'fields': ('is_published', 'status', 'is_premium', 'premium_until', 'list_date', 'expiry_date')
        }),
    )
