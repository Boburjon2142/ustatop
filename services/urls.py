from django.urls import path
from .views import (
    HomeView,
    CategoryListView,
    CategoryDetailView,
    service_suggestions,
    service_details,
    category_services,
)

app_name = 'services'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('services/suggestions/', service_suggestions, name='service_suggestions'),
    path('services/details/', service_details, name='service_details'),
    path('services/by-category/', category_services, name='category_services'),
]
