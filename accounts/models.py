from io import BytesIO
from pathlib import Path

from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    class Roles(models.TextChoices):
        CLIENT = 'CLIENT', 'Mijoz'
        PROVIDER = 'PROVIDER', 'Usta'
        ADMIN = 'ADMIN', 'Administrator'

    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CLIENT)
    is_phone_verified = models.BooleanField(default=False)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def is_provider(self):
        return self.role == self.Roles.PROVIDER

    def is_admin(self):
        return self.role == self.Roles.ADMIN or self.is_superuser


class RegistrationToken(models.Model):
    class TokenType(models.TextChoices):
        REGISTER = 'REGISTER', 'Register'
        RESET = 'RESET', 'Reset'

    username = models.CharField(max_length=150)
    token_type = models.CharField(max_length=10, choices=TokenType.choices)
    link_code = models.CharField(max_length=12)
    otp_code = models.CharField(max_length=6)
    telegram_id = models.BigIntegerField(null=True, blank=True)
    payload = models.JSONField()
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    district = models.CharField(max_length=120)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.avatar and not self.avatar.name.lower().endswith('.webp'):
            self.avatar.file.seek(0)
            img = Image.open(self.avatar)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            buffer = BytesIO()
            img.save(buffer, format='WEBP', quality=80, method=6)
            new_name = Path(self.avatar.name).with_suffix('.webp').name
            self.avatar.save(new_name, ContentFile(buffer.getvalue()), save=False)
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            full_name=instance.get_full_name() or instance.username,
            city='Toshkent',
            district='Markaz',
        )
