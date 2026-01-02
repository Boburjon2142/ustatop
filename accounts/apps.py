import os
import threading

from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command

_polling_started = False


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        global _polling_started
        if _polling_started:
            return
        if not settings.DEBUG:
            return
        if not getattr(settings, 'TELEGRAM_USE_POLLING', False):
            return
        if os.environ.get('RUN_MAIN') != 'true':
            return
        if os.environ.get('DISABLE_TELEGRAM_POLLING') == '1':
            return
        if not getattr(settings, 'TELEGRAM_BOT_TOKEN', ''):
            return

        def _run():
            call_command('telegram_polling')

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        _polling_started = True
