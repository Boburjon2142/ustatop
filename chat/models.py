from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image

from listings.models import Listing
from providers.models import Provider


class ChatThread(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Ochiq'
        CLOSED = 'CLOSED', 'Yopiq'

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_threads',
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)

    def __str__(self):
        if self.listing:
            return f"Thread {self.id} - {self.listing.title}"
        return f"Thread {self.id} - {self.provider.user.username}"


class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.ImageField(upload_to='chat_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} by {self.sender.username}"

    def save(self, *args, **kwargs):
        if self.attachment and not self.attachment.name.lower().endswith('.webp'):
            self.attachment.file.seek(0)
            img = Image.open(self.attachment)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            buffer = BytesIO()
            img.save(buffer, format='WEBP', quality=80, method=6)
            new_name = Path(self.attachment.name).with_suffix('.webp').name
            self.attachment.save(new_name, ContentFile(buffer.getvalue()), save=False)
        super().save(*args, **kwargs)
