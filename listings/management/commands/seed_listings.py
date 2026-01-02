import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from listings.models import Listing
from providers.models import Provider
from services.models import Category, Service


class Command(BaseCommand):
    help = 'Seed 14 approved listings.'

    def handle(self, *args, **options):
        if not Category.objects.exists() or not Service.objects.exists():
            self.stdout.write(self.style.WARNING('Run seed_categories_services first.'))
            return

        User = get_user_model()
        providers = []
        for idx in range(1, 6):
            username = f'usta{idx}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'role': User.Roles.PROVIDER},
            )
            if created:
                user.set_password('password123')
                user.save()
                user.profile.full_name = f'Usta {idx}'
                user.profile.city = 'Toshkent'
                user.profile.district = 'Markaz'
                user.profile.save()
            provider, _ = Provider.objects.get_or_create(user=user)
            providers.append(provider)

        cities = ['Toshkent', 'Samarqand', 'Buxoro', 'Farg‘ona', 'Namangan']
        titles = [
            'Tez va sifatli xizmat',
            'Usta xizmatlari',
            'Ishonchli usta',
            'Sifatli ta’mir',
            'Professional yordam',
            '24/7 xizmat',
            'Uy ta’miri ustasi',
            'Elektrik xizmatlari',
            'Santexnik usta',
            'Tozalash xizmati',
            'Konditsioner ta’miri',
            'Muzlatgich ustasi',
            'Gipsokarton ishlari',
            'Plitka ustasi',
        ]

        services = list(Service.objects.select_related('category'))
        existing_count = Listing.objects.count()
        if existing_count >= 14:
            self.stdout.write(self.style.WARNING('Listings already exist (14 or more).'))
            return

        to_create = 14 - existing_count
        for i in range(to_create):
            service = services[i % len(services)]
            Listing.objects.create(
                provider=random.choice(providers),
                category=service.category,
                service=service,
                title=titles[i],
                description='Tajribali usta, tez va sifatli xizmat ko‘rsatadi.',
                city=cities[i % len(cities)],
                district='',
                price_from=50000 + (i * 10000),
                status=Listing.Status.APPROVED,
                is_public=True,
                approved_at=timezone.now(),
            )

        self.stdout.write(self.style.SUCCESS(f'Seeded {to_create} listings.'))
