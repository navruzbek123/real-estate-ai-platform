from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.timezone import now
from datetime import timedelta


class UserAccountManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, password, **extra_fields)


class UserAccount(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('agent', 'Agent'),
        ('premium', 'Premium User'),
        ('free', 'Free User'),
    ]

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='free')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    ai_estimations_today = models.IntegerField(default=0)
    ai_estimations_this_month = models.IntegerField(default=0)
    last_ai_estimation_date = models.DateField(null=True, blank=True)
    ai_estimation_reset_date = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(default=now)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __str__(self):
        return self.email

    def get_role_display_name(self):
        role_names = {
            'admin': 'Administrator',
            'agent': 'Agent',
            'premium': 'Premium Foydalanuvchi',
            'free': 'Bepul Foydalanuvchi',
        }
        return role_names.get(self.role, 'Noma\'lum')

    def get_monthly_ai_limit(self):
        if self.role == 'agent':
            return float('inf')
        elif self.role == 'premium':
            return 20
        else:
            return 3

    def get_daily_ai_limit(self):
        if self.role == 'agent':
            return float('inf')
        elif self.role == 'premium':
            return 10
        else:
            return 3

    def can_use_ai_estimation(self):
        today = now().date()
        month_start = today.replace(day=1)

        if self.last_ai_estimation_date != today:
            self.ai_estimations_today = 0
            self.last_ai_estimation_date = today
            self.save(update_fields=['ai_estimations_today', 'last_ai_estimation_date'])

        if not self.ai_estimation_reset_date or self.ai_estimation_reset_date < month_start:
            self.ai_estimations_this_month = 0
            self.ai_estimation_reset_date = month_start
            self.save(update_fields=['ai_estimations_this_month', 'ai_estimation_reset_date'])

        daily_limit = self.get_daily_ai_limit()
        monthly_limit = self.get_monthly_ai_limit()

        if daily_limit != float('inf') and self.ai_estimations_today >= daily_limit:
            return False, f"kunlik_limit"
        if monthly_limit != float('inf') and self.ai_estimations_this_month >= monthly_limit:
            return False, f"oylik_limit"

        return True, ""

    def increment_ai_estimation(self):
        today = now().date()
        month_start = today.replace(day=1)

        if self.last_ai_estimation_date != today:
            self.ai_estimations_today = 0
            self.last_ai_estimation_date = today

        if not self.ai_estimation_reset_date or self.ai_estimation_reset_date < month_start:
            self.ai_estimations_this_month = 0
            self.ai_estimation_reset_date = month_start

        self.ai_estimations_today += 1
        self.ai_estimations_this_month += 1
        self.save(update_fields=[
            'ai_estimations_today',
            'ai_estimations_this_month',
            'last_ai_estimation_date',
            'ai_estimation_reset_date'
        ])

    def get_listing_limit(self):
        if self.role == 'agent':
            return float('inf')
        elif self.role == 'premium':
            return 10
        else:
            return 3

    def has_reached_listing_limit(self, current_count):
        limit = self.get_listing_limit()
        if limit == float('inf'):
            return False
        return current_count >= limit


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('ai_estimation', 'AI Baholash'),
        ('message', 'Xabar'),
        ('listing_expiry', 'E\'lon Muddati'),
        ('premium', 'Premium Status'),
        ('system', 'Tizim Xabari'),
    ]

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])


class UserProfile(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='profile')
    favorite_districts = models.JSONField(default=list, blank=True)
    preferred_property_types = models.JSONField(default=list, blank=True)
    price_range_min = models.IntegerField(default=0)
    price_range_max = models.IntegerField(default=100000000)
    notifications_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile - {self.user.email}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_unread_count(self):
        return self.user.notifications.filter(is_read=False).count()


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


models.signals.post_save.connect(create_user_profile, sender=UserAccount)
