from django.contrib import admin
from .models import Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'free_listing_credits', 'rating', 'total_reviews', 'is_active')
