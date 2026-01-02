import json
import random
import string
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import FormView

from providers.models import Provider
from .forms import (
    LoginForm,
    RegistrationStartForm,
    VerificationCodeForm,
    PasswordResetRequestForm,
    PasswordResetConfirmForm,
)
from .models import RegistrationToken
from .utils import send_telegram_message

User = get_user_model()


class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegistrationStartForm
    success_url = reverse_lazy('accounts:verify')

    def form_valid(self, form):
        link_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        otp_code = f"{random.randint(100000, 999999)}"
        RegistrationToken.objects.create(
            username=form.cleaned_data['username'],
            token_type=RegistrationToken.TokenType.REGISTER,
            link_code=link_code,
            otp_code=otp_code,
            payload={
                'phone_number': form.cleaned_data['phone_number'],
                'role': form.cleaned_data['role'],
                'full_name': form.cleaned_data['full_name'],
                'city': form.cleaned_data['city'],
                'password_hash': make_password(form.cleaned_data['password1']),
            },
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        messages.success(self.request, 'Telegram orqali tasdiqlash uchun kod yaratildi.')
        return redirect(self.get_success_url() + f"?username={form.cleaned_data['username']}")


class VerifyEmailView(FormView):
    template_name = 'accounts/verify.html'
    form_class = VerificationCodeForm
    success_url = reverse_lazy('services:home')

    def dispatch(self, request, *args, **kwargs):
        username = request.GET.get('username', '').strip()
        if not username:
            messages.error(request, 'Avval ro‘yxatdan o‘ting.')
            return redirect('accounts:register')
        self.registration = (
            RegistrationToken.objects.filter(
                username=username,
                token_type=RegistrationToken.TokenType.REGISTER,
                used_at__isnull=True,
            )
            .order_by('-created_at')
            .first()
        )
        if not self.registration or self.registration.is_expired():
            messages.error(request, 'Tasdiqlash muddati tugagan. Qayta urinib ko‘ring.')
            return redirect('accounts:register')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.cleaned_data['code'] != self.registration.otp_code:
            form.add_error('code', 'Kod noto‘g‘ri.')
            return self.form_invalid(form)

        if not self.registration.telegram_id:
            form.add_error('code', 'Telegram bog‘lanmagan. Avval botga kod yuboring.')
            return self.form_invalid(form)

        payload = self.registration.payload
        username = self.registration.username
        user = User.objects.create_user(
            username=username,
            role=payload['role'],
            phone_number=payload['phone_number'],
        )
        user.password = payload['password_hash']
        user.telegram_id = self.registration.telegram_id
        user.save()
        profile = user.profile
        profile.full_name = payload['full_name']
        profile.city = payload['city']
        profile.save()

        if user.role == User.Roles.PROVIDER:
            Provider.objects.get_or_create(user=user)

        login(self.request, user)
        self.registration.used_at = timezone.now()
        self.registration.save()
        messages.success(self.request, 'Hisob tasdiqlandi va yaratildi.')
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registration'] = self.registration
        context['bot_username'] = getattr(settings, 'TELEGRAM_BOT_USERNAME', '')
        return context


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated and user.is_provider():
            return reverse_lazy('dashboard:provider_home')
        return reverse_lazy('services:home')


def logout_view(request):
    logout(request)
    return redirect('services:home')


class PasswordResetRequestView(FormView):
    template_name = 'accounts/password_reset_request.html'
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy('accounts:password_reset_confirm')

    def form_valid(self, form):
        link_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        otp_code = f"{random.randint(100000, 999999)}"
        RegistrationToken.objects.create(
            username=form.cleaned_data['username'],
            token_type=RegistrationToken.TokenType.RESET,
            link_code=link_code,
            otp_code=otp_code,
            payload={},
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        messages.success(self.request, 'Telegram orqali tiklash uchun kod yaratildi.')
        return redirect(self.get_success_url() + f"?username={form.cleaned_data['username']}")


class PasswordResetConfirmView(FormView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = PasswordResetConfirmForm
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        username = request.GET.get('username', '').strip()
        if not username:
            messages.error(request, 'Avval username kiriting.')
            return redirect('accounts:password_reset')
        self.reset_token = (
            RegistrationToken.objects.filter(
                username=username,
                token_type=RegistrationToken.TokenType.RESET,
                used_at__isnull=True,
            )
            .order_by('-created_at')
            .first()
        )
        if not self.reset_token or self.reset_token.is_expired():
            messages.error(request, 'Tiklash muddati tugagan. Qayta urinib ko‘ring.')
            return redirect('accounts:password_reset')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.cleaned_data['code'] != self.reset_token.otp_code:
            form.add_error('code', 'Kod noto‘g‘ri.')
            return self.form_invalid(form)
        if not self.reset_token.telegram_id:
            form.add_error('code', 'Telegram bog‘lanmagan. Avval botga kod yuboring.')
            return self.form_invalid(form)

        user = User.objects.filter(username=self.reset_token.username).first()
        if not user or user.telegram_id != self.reset_token.telegram_id:
            form.add_error('code', 'Telegram tasdiqlanmadi.')
            return self.form_invalid(form)

        user.set_password(form.cleaned_data['password1'])
        user.save()
        self.reset_token.used_at = timezone.now()
        self.reset_token.save()
        messages.success(self.request, 'Parol yangilandi. Endi kirishingiz mumkin.')
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reset_token'] = self.reset_token
        context['bot_username'] = getattr(settings, 'TELEGRAM_BOT_USERNAME', '')
        return context


def process_telegram_update(payload):
    message = payload.get('message') or {}
    text = message.get('text', '')
    chat = message.get('chat') or {}
    telegram_id = chat.get('id')
    if not text or not telegram_id:
        return

    parts = text.strip().split()
    if parts[0].lower() != '/start' or len(parts) < 2:
        send_telegram_message(telegram_id, 'Tasdiqlash uchun /start KOD yuboring.')
        return

    link_code = parts[1].strip().upper()
    token = (
        RegistrationToken.objects.filter(link_code=link_code, used_at__isnull=True)
        .order_by('-created_at')
        .first()
    )
    if not token or token.is_expired():
        send_telegram_message(telegram_id, 'Kod noto‘g‘ri yoki muddati tugagan.')
        return

    if token.token_type == RegistrationToken.TokenType.RESET:
        user = User.objects.filter(username=token.username).first()
        if not user or not user.telegram_id:
            send_telegram_message(telegram_id, 'Bu username Telegram bilan bog‘lanmagan.')
            return
        if user.telegram_id != telegram_id:
            send_telegram_message(telegram_id, 'Bu kod sizga tegishli emas.')
            return
    elif User.objects.filter(telegram_id=telegram_id).exists():
        send_telegram_message(telegram_id, 'Bu Telegram allaqachon boshqa profilga bog‘langan.')
        return

    token.telegram_id = telegram_id
    token.save()
    send_telegram_message(
        telegram_id,
        f"Tasdiqlash kodi: {token.otp_code}\n5 daqiqada eskiradi.",
    )


@csrf_exempt
def telegram_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    process_telegram_update(payload)
    return HttpResponse(status=200)

# Create your views here.
