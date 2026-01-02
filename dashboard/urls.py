from django.urls import path
from .views import provider_home, pending_listings, listing_review, provider_list

app_name = 'dashboard'

urlpatterns = [
    path('provider/', provider_home, name='provider_home'),
    path('admin/pending/', pending_listings, name='pending_listings'),
    path('admin/listings/<int:pk>/', listing_review, name='listing_review'),
    path('admin/providers/', provider_list, name='provider_list'),
]
