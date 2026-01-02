from django.views.generic import DetailView
from listings.models import Listing
from .models import Provider


class ProviderDetailView(DetailView):
    model = Provider
    template_name = 'providers/provider_detail.html'
    context_object_name = 'provider'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listings'] = Listing.objects.filter(provider=self.object, is_public=True)
        return context

# Create your views here.
