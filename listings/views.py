from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.db.models import Q, Count

from chat.models import ChatThread
from providers.models import Provider
from .forms import ListingForm, listing_image_formset
from .models import Listing
from services.models import ServiceDetail, Service


class ProviderRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_provider()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Faqat ustalar uchun.')
            return redirect('services:home')
        return super().handle_no_permission()


class PublicListingListView(ListView):
    model = Listing
    template_name = 'listings/listing_list.html'
    context_object_name = 'listings'

    def _resolve_service_id(self):
        if hasattr(self, '_resolved_service_id'):
            return self._resolved_service_id
        service_id = self.request.GET.get('service_id', '').strip()
        query = self.request.GET.get('q', '').strip()
        if not service_id and query:
            service = Service.objects.filter(name__icontains=query).order_by('name').first()
            if service:
                service_id = str(service.id)
        self._resolved_service_id = service_id
        return service_id

    def get_queryset(self):
        queryset = Listing.objects.filter(is_public=True)
        query = self.request.GET.get('q', '').strip()
        service_id = self._resolve_service_id()
        detail_ids = self.request.GET.getlist('detail')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(service__name__icontains=query)
                | Q(category__name__icontains=query)
                | Q(provider__user__profile__full_name__icontains=query)
            ).distinct()
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        if detail_ids:
            queryset = queryset.filter(service_details__id__in=detail_ids)
            queryset = queryset.distinct()
            queryset = queryset.annotate(
                match_count=Count(
                    'service_details',
                    filter=Q(service_details__id__in=detail_ids),
                    distinct=True,
                )
            ).order_by('-match_count', '-provider__rating')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        context['service_id'] = self._resolve_service_id()
        context['selected_details'] = self.request.GET.getlist('detail')
        if context['service_id']:
            details = (
                ServiceDetail.objects.filter(service_id=context['service_id'])
                .order_by('question', 'name')
                .values('id', 'name', 'question')
            )
            grouped = {}
            for detail in details:
                grouped.setdefault(detail['question'] or 'Umumiy', []).append(
                    {'id': detail['id'], 'name': detail['name']}
                )
            context['service_details'] = (
                ServiceDetail.objects.filter(service_id=context['service_id']).order_by('name')
            )
            context['service_detail_groups'] = [
                {'question': question, 'options': options} for question, options in grouped.items()
            ]
        else:
            context['service_details'] = []
            context['service_detail_groups'] = []
        return context


class ListingDetailView(DetailView):
    model = Listing
    template_name = 'listings/listing_detail.html'
    context_object_name = 'listing'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_admin():
            return Listing.objects.all()
        if user.is_authenticated and hasattr(user, 'provider'):
            return Listing.objects.filter(provider=user.provider)
        return Listing.objects.filter(is_public=True)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ProviderListingCreateView(LoginRequiredMixin, ProviderRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm
    template_name = 'listings/listing_form.html'

    def get_success_url(self):
        return reverse('dashboard:provider_home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = listing_image_formset(3)(self.request.POST, self.request.FILES)
        else:
            context['formset'] = listing_image_formset(3)()
        return context

    def form_valid(self, form):
        provider = Provider.objects.get(user=self.request.user)
        form.instance.provider = provider
        form.instance.status = Listing.Status.DRAFT
        form.instance.is_public = False

        context = self.get_context_data()
        formset = context['formset']
        with transaction.atomic():
            self.object = form.save()
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
        messages.success(self.request, 'E’lon saqlandi.')
        return redirect(self.get_success_url())


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ProviderListingUpdateView(LoginRequiredMixin, ProviderRequiredMixin, UpdateView):
    model = Listing
    form_class = ListingForm
    template_name = 'listings/listing_form.html'

    def get_queryset(self):
        return Listing.objects.filter(provider__user=self.request.user)

    def get_success_url(self):
        return reverse('dashboard:provider_home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra = max(0, 3 - self.object.images.count())
        if self.request.POST:
            context['formset'] = listing_image_formset(extra)(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context['formset'] = listing_image_formset(extra)(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        with transaction.atomic():
            self.object = form.save()
            if formset.is_valid():
                formset.save()
        messages.success(self.request, 'E’lon yangilandi.')
        return redirect(self.get_success_url())


@login_required
def request_approval(request, pk):
    listing = get_object_or_404(Listing, pk=pk, provider__user=request.user)
    if listing.status not in [Listing.Status.DRAFT, Listing.Status.REJECTED]:
        messages.error(request, 'E’lon yuborish mumkin emas.')
        return redirect('dashboard:provider_home')

    listing.status = Listing.Status.PENDING
    listing.is_public = False
    listing.rejection_reason = ''
    listing.save()

    ChatThread.objects.get_or_create(listing=listing, provider=listing.provider)
    messages.success(request, 'Tasdiq uchun yuborildi.')
    return redirect('dashboard:provider_home')

# Create your views here.
