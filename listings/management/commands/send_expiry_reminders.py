from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from listings.models import Listing
from accounts.models import Notification
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Отправка напоминаний о скором истечении срока объявлений'

    def handle(self, *args, **options):
        now = timezone.now()
        reminder_date = now + timedelta(days=3)

        listings_to_remind = Listing.objects.filter(
            expiry_date__lte=reminder_date,
            expiry_date__gt=now,
            status='active',
            reminder_sent=False
        )

        count = listings_to_remind.count()
        self.stdout.write(f'Найдено {count} объявлений для напоминания')

        for listing in listings_to_remind:
            days_left = (listing.expiry_date - now).days

            if listing.user:
                Notification.objects.create(
                    user=listing.user,
                    notification_type='listing_expiry',
                    title='Срок объявления скоро истекает',
                    message=f'Ваше объявление "{listing.title}" истекает через {days_left} дней. Продлите или обновите его!',
                    link=f'/listings/{listing.slug}/'
                )

                listing.reminder_sent = True
                listing.save(update_fields=['reminder_sent'])

                if listing.user.profile.email_notifications:
                    try:
                        send_mail(
                            subject=f'Напоминание: срок объявления истекает',
                            message=f'''Здравствуйте, {listing.user.name}!

Ваше объявление "{listing.title}" истекает через {days_left} дней ({listing.expiry_date.strftime('%d.%m.%Y')}).

Продлите или обновите объявление, чтобы оно оставалось видимым.

С уважением,
Команда сайта недвижимости''',
                            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
                            recipient_list=[listing.user.email],
                            fail_silently=True
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f'Напоминание отправлено: {listing.title}')
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Ошибка отправки email: {e}')
                        )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Объявление без пользователя: {listing.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Обработано {count} объявлений')
        )
