from django.conf import settings
from django.db import models
from services.models import Category, Service


class Provider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, blank=True)
    services = models.ManyToManyField(Service, blank=True)
    rating = models.FloatField(default=0)
    total_reviews = models.IntegerField(default=0)
    free_listing_credits = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
