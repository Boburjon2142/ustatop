# Ustatop (MVP)

Service marketplace for Uzbekistan built with Django 4.2+ and Bootstrap 5.

## Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install django psycopg2-binary pillow
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_categories_services
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Notes
- SQLite is default for local dev; configure PostgreSQL in `ustago/settings.py` if needed.
- Providers get 3 free listing credits; approval consumes 1 credit.
- Listings are public only when status is APPROVED.
- Ro‘yxatdan o‘tish va parol tiklash Telegram orqali tasdiqlanadi.
- Telegram uchun `ustago/settings.py` ichida `TELEGRAM_BOT_TOKEN` va `TELEGRAM_BOT_USERNAME` ni to‘ldiring.
- Webhook: `https://your-domain/accounts/telegram/webhook/`
- Lokal uchun: alohida terminalda `python manage.py telegram_polling` ishga tushiring (webhook kerak emas).

## Tests

```bash
python manage.py test
```
