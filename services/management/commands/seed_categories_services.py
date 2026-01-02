from django.core.management.base import BaseCommand
from services.models import Category, Service


class Command(BaseCommand):
    help = 'Seed sample Uzbek categories and services.'

    def handle(self, *args, **options):
        data = {
            'Usta ustalar': [
                'Santexnik',
                'Elektrik',
                'Bo‘yoqchi',
            ],
            'Uskuna xizmatlari': [
                'Konditsioner ta’miri',
                'Muzlatgich ta’miri',
                'Kir yuvish mashinasi',
            ],
            'Uy ta’miri': [
                'Plitka ishlari',
                'Gipsokarton',
                'Shift ishlari',
            ],
            'Tozalash': [
                'Uy tozalash',
                'Ofis tozalash',
            ],
        }

        detail_map = {
            'Santexnik': {
                'Muammo turi': ['Quvur almashtirish', 'Kran ta’miri', 'Dush o‘rnatish'],
                'Joylashuv': ['Oshxona', 'Hammom', 'Hovli'],
            },
            'Elektrik': {
                'Ish turi': ['Rozetka o‘rnatish', 'Chiroq o‘rnatish', 'Sim tortish'],
                'Joylashuv': ['Uy', 'Ofis', 'Sanoat'],
            },
            'Bo‘yoqchi': {
                'Sirt turi': ['Ichki bo‘yoq', 'Tashqi bo‘yoq', 'Laklash'],
                'Maydon': ['Kichik xona', 'Butun uy'],
            },
            'Konditsioner ta’miri': {
                'Xizmat turi': ['Gaz to‘ldirish', 'Tozalash', 'Montaj'],
                'Muammo': ['Sovutmayapti', 'Shovqin'],
            },
            'Muzlatgich ta’miri': {
                'Muammo': ['Motor ta’miri', 'Freon to‘ldirish'],
            },
            'Kir yuvish mashinasi': {
                'Muammo': ['Podshipnik almashtirish', 'Nasos ta’miri'],
            },
            'Plitka ishlari': {
                'Sirt': ['Devorga plitka', 'Polga plitka'],
            },
            'Gipsokarton': {
                'Ish turi': ['Devor bo‘limi', 'Shift'],
            },
            'Shift ishlari': {
                'Turi': ['Natyojnoy shift', 'Gipsli shift'],
            },
            'Uy tozalash': {
                'Turi': ['General tozalash', 'Oynalar yuvish'],
            },
            'Ofis tozalash': {
                'Reja': ['Kundalik tozalash', 'Haftalik tozalash'],
            },
        }

        for category_name, services in data.items():
            category, _ = Category.objects.get_or_create(name=category_name, defaults={'slug': ''})
            for service_name in services:
                Service.objects.get_or_create(
                    category=category,
                    name=service_name,
                    defaults={'description': f'{service_name} bo‘yicha xizmat.'},
                )

        from services.models import ServiceDetail

        for service_name, questions in detail_map.items():
            try:
                service = Service.objects.get(name=service_name)
            except Service.DoesNotExist:
                continue
            for question, details in questions.items():
                for detail in details:
                    ServiceDetail.objects.get_or_create(
                        service=service,
                        question=question,
                        name=detail,
                    )

        self.stdout.write(self.style.SUCCESS('Seed data created.'))
