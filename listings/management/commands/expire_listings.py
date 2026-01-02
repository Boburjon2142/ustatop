from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from chat.models import ChatThread
from listings.models import Listing


class Command(BaseCommand):
    help = 'Move approved listings older than N days back to pending for re-approval.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff = timezone.now() - timedelta(days=days)

        listings = Listing.objects.filter(
            status=Listing.Status.APPROVED,
            is_public=True,
            approved_at__isnull=False,
            approved_at__lte=cutoff,
        ).select_related('provider')

        count = listings.count()
        if dry_run:
            self.stdout.write(self.style.WARNING(f'{count} listing(s) would be moved to PENDING.'))
            return

        for listing in listings:
            listing.status = Listing.Status.PENDING
            listing.is_public = False
            listing.rejection_reason = ''
            listing.approved_at = None
            listing.save()
            ChatThread.objects.get_or_create(listing=listing, provider=listing.provider)

        self.stdout.write(self.style.SUCCESS(f'Moved {count} listing(s) to PENDING.'))
