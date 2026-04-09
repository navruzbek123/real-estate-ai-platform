from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from listings.models import Listing
from accounts.models import Notification


class Command(BaseCommand):
    help = 'Проверка истекших объявлений и их архивация'

    def handle(self, *args, **options):
        now = timezone.now()
        expired_listings = Listing.objects.filter(
            expiry_date__lt=now,
            status__in=['active', 'pending']
        )

        count = expired_listings.count()
        self.stdout.write(f'Найдено {count} истекших объявлений')

        for listing in expired_listings:
            listing.status = 'archived'
            listing.is_published = False
            listing.save(update_fields=['status', 'is_published'])

            self.stdout.write(
                self.style.WARNING(f'Архивировано: {listing.title} (ID: {listing.id})')
            )

            if listing.user:
                Notification.objects.create(
                    user=listing.user,
                    notification_type='listing_expiry',
                    title='Срок объявления истек',
                    message=f'Ваше объявление "{listing.title}" было архивировано из-за истечения срока (30 дней)',
                    link=f'/listings/{listing.slug}/'
                )

        self.stdout.write(
            self.style.SUCCESS(f'Успешно обработано {count} объявлений')
        )
