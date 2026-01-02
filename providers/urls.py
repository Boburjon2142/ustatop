from django.urls import path
from .views import ProviderDetailView

app_name = 'providers'

urlpatterns = [
    path('<int:pk>/', ProviderDetailView.as_view(), name='provider_detail'),
]
