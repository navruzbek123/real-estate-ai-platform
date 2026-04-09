from django.core.management.base import BaseCommand
from listings.models import Listing
from listings.yandex_maps import YandexMapsService


class Command(BaseCommand):
    help = 'Update coordinates for all listings without latitude/longitude'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        listings = Listing.objects.filter(latitude__isnull=True, longitude__isnull=True)
        total = listings.count()
        
        self.stdout.write(f'Found {total} listings without coordinates')
        
        if options['dry_run']:
            for listing in listings[:10]:
                self.stdout.write(f'  - {listing.title}: {listing.address}, {listing.city}')
            return
        
        updated = 0
        failed = 0
        
        for listing in listings:
            full_address = f"{listing.address}, {listing.city}, {listing.state} {listing.zipcode}"
            self.stdout.write(f'Geocoding: {full_address}')
            
            coords = YandexMapsService.geocode(full_address)
            
            if coords:
                listing.latitude = coords['latitude']
                listing.longitude = coords['longitude']
                listing.save(update_fields=['latitude', 'longitude'])
                updated += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  Updated: {listing.title} -> {coords}')
                )
            else:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(f'  Failed: {listing.title}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nCompleted: {updated} updated, {failed} failed')
        )
