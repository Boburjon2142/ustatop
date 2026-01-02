from django.urls import path
from .views import start_provider_chat, thread_detail

app_name = 'chat'

urlpatterns = [
    path('providers/<int:provider_id>/start/', start_provider_chat, name='start_provider_chat'),
    path('threads/<int:pk>/', thread_detail, name='thread_detail'),
]
