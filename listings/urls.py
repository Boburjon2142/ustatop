from django.urls import path
from .views import (
    PublicListingListView,
    ListingDetailView,
    ProviderListingCreateView,
    ProviderListingUpdateView,
    request_approval,
)

app_name = 'listings'

urlpatterns = [
    path('', PublicListingListView.as_view(), name='public_list'),
    path('create/', ProviderListingCreateView.as_view(), name='create'),
    path('<int:pk>/', ListingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', ProviderListingUpdateView.as_view(), name='edit'),
    path('<int:pk>/request-approval/', request_approval, name='request_approval'),
]
