from django.http import JsonResponse
from django.views.generic import DetailView, ListView, TemplateView
from listings.models import Listing
from .models import Category, Service, ServiceDetail


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()[:8]
        context['featured_listings'] = Listing.objects.filter(is_public=True)[:6]
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'services/category_list.html'
    context_object_name = 'categories'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'services/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


def service_suggestions(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    services = (
        Service.objects.filter(name__icontains=query)
        .select_related('category')
        .order_by('name')[:8]
    )
    results = [
        {
            'id': service.id,
            'name': service.name,
            'category': service.category.name,
        }
        for service in services
    ]
    return JsonResponse({'results': results})


def service_details(request):
    service_id = request.GET.get('service_id')
    if not service_id:
        return JsonResponse({'results': []})
    details = (
        ServiceDetail.objects.filter(service_id=service_id)
        .order_by('question', 'name')
        .values('id', 'name', 'question')
    )
    grouped = {}
    for detail in details:
        grouped.setdefault(detail['question'] or 'Umumiy', []).append(
            {'id': detail['id'], 'name': detail['name']}
        )
    results = [{'question': question, 'options': options} for question, options in grouped.items()]
    return JsonResponse({'results': results})


def category_services(request):
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({'results': []})
    services = (
        Service.objects.filter(category_id=category_id)
        .order_by('name')
        .values('id', 'name')
    )
    return JsonResponse({'results': list(services)})

# Create your views here.
