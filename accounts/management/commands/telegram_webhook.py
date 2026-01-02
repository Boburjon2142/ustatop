import json
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Set or delete Telegram webhook.'

    def add_arguments(self, parser):
        parser.add_argument('--set', action='store_true', help='Set webhook URL.')
        parser.add_argument('--delete', action='store_true', help='Delete webhook.')
        parser.add_argument('--url', type=str, default='', help='Webhook URL.')

    def handle(self, *args, **options):
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if not token:
            self.stderr.write('TELEGRAM_BOT_TOKEN is empty.')
            return

        if options['delete']:
            url = f"https://api.telegram.org/bot{token}/deleteWebhook"
        elif options['set']:
            if not options['url']:
                self.stderr.write('Provide --url for --set.')
                return
            encoded = urllib.parse.quote(options['url'], '')
            url = f"https://api.telegram.org/bot{token}/setWebhook?url={encoded}"
        else:
            self.stderr.write('Use --set or --delete.')
            return

        request = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        self.stdout.write(json.dumps(data))
