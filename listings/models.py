from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.db import models
from PIL import Image

from providers.models import Provider
from services.models import Category, Service, ServiceDetail


class Listing(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Qoralama'
        PENDING = 'PENDING', 'Kutilmoqda'
        APPROVED = 'APPROVED', 'Tasdiqlangan'
        REJECTED = 'REJECTED', 'Rad etilgan'

    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='listings')
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    service_details = models.ManyToManyField(ServiceDetail, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    city = models.CharField(max_length=120)
    district = models.CharField(max_length=120, blank=True, default='')
    price_from = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    rejection_reason = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listing_images/', verbose_name='Rasm')

    def __str__(self):
        return f"Image for {self.listing.title}"

    def save(self, *args, **kwargs):
        if self.image and not self.image.name.lower().endswith('.webp'):
            self.image.file.seek(0)
            img = Image.open(self.image)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            buffer = BytesIO()
            img.save(buffer, format='WEBP', quality=80, method=6)
            new_name = Path(self.image.name).with_suffix('.webp').name
            self.image.save(new_name, ContentFile(buffer.getvalue()), save=False)
        super().save(*args, **kwargs)
