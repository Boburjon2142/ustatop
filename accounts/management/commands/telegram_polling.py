import json
import time
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from accounts.views import process_telegram_update


class Command(BaseCommand):
    help = 'Poll Telegram updates for local dev (no webhook).'

    def handle(self, *args, **options):
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if not token:
            self.stderr.write('TELEGRAM_BOT_TOKEN is empty.')
            return

        offset = 0
        self.stdout.write('Polling Telegram updates... Press Ctrl+C to stop.')
        while True:
            try:
                url = (
                    'https://api.telegram.org/bot'
                    + token
                    + '/getUpdates?timeout=25&offset='
                    + str(offset)
                )
                with urllib.request.urlopen(url, timeout=30) as response:
                    data = json.loads(response.read().decode('utf-8'))
                for update in data.get('result', []):
                    offset = update.get('update_id', 0) + 1
                    process_telegram_update(update)
            except Exception as exc:
                self.stderr.write(str(exc))
                time.sleep(2)
