from django.db import models
from django.utils.timezone import now
from realtors.models import Realtor


class Listing(models.Model):
    class SaleType(models.TextChoices):
        FOR_SALE = 'For Sale'
        FOR_RENT = 'For Rent'

    class HomeType(models.TextChoices):
        HOUSE = 'House'
        CONDO = 'Condo'
        TOWNHOUSE = 'Townhouse'

    class StatusType(models.TextChoices):
        ACTIVE = 'active'
        PENDING = 'pending'
        SOLD = 'sold'
        ARCHIVED = 'archived'

    realtor = models.ForeignKey(Realtor, on_delete=models.DO_NOTHING)
    user = models.ForeignKey('accounts.UserAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='listings')
    slug = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=15)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    description = models.TextField(blank=True)
    sale_type = models.CharField(max_length=50, choices=SaleType.choices, default=SaleType.FOR_SALE)
    price = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.DecimalField(max_digits=2, decimal_places=1)
    home_type = models.CharField(max_length=50, choices=HomeType.choices, default=HomeType.HOUSE)
    sqft = models.IntegerField()
    open_house = models.BooleanField(default=False)
    photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/')
    photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_4 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_5 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_6 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_7 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_8 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_9 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_10 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_11 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_12 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_13 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_14 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_15 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_16 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_17 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_18 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_19 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_20 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    is_published = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=StatusType.choices, default=StatusType.ACTIVE)
    is_premium = models.BooleanField(default=False)
    premium_until = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)
    list_date = models.DateTimeField(default=now, blank=True)

    class Meta:
        ordering = ['-is_premium', '-list_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.expiry_date and self.list_date:
            from datetime import timedelta
            self.expiry_date = self.list_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def is_expired(self):
        if self.expiry_date and now() > self.expiry_date:
            return True
        return False

    def days_until_expiry(self):
        if self.expiry_date:
            delta = self.expiry_date - now()
            return max(0, delta.days)
        return 30

    def should_send_reminder(self):
        if self.expiry_date and not self.reminder_sent:
            days_left = self.days_until_expiry()
            return 0 < days_left <= 3
        return False

    def get_main_photo(self):
        if self.photo_main:
            return self.photo_main.url
        return '/static/img/no-photo.png'

    def get_photo_count(self):
        count = 0
        for i in range(1, 21):
            photo = getattr(self, f'photo_{i}', None)
            if photo:
                count += 1
        return count

    def get_district(self):
        return self.city

    def get_price_per_sqm(self):
        if self.sqft > 0:
            return self.price / self.sqft
        return 0

    def get_floor_info(self):
        return f"1/5"

    def get_favorite_count(self):
        return self.favorites.count()

    def get_message_count(self):
        return self.messages.count()
