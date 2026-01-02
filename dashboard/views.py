from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from listings.models import Listing
from providers.models import Provider


def is_admin(user):
    return user.is_authenticated and user.is_admin()


@login_required
def provider_home(request):
    if not request.user.is_provider():
        messages.error(request, 'Faqat ustalar uchun.')
        return redirect('services:home')

    provider = get_object_or_404(Provider, user=request.user)
    listings = Listing.objects.filter(provider=provider).order_by('-created_at')
    return render(
        request,
        'dashboard/provider_home.html',
        {'provider': provider, 'listings': listings},
    )


@user_passes_test(is_admin)
def pending_listings(request):
    listings = Listing.objects.filter(status=Listing.Status.PENDING).order_by('created_at')
    return render(request, 'dashboard/pending_listings.html', {'listings': listings})


@user_passes_test(is_admin)
def listing_review(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    provider = listing.provider

    if request.method == 'POST':
        action = request.POST.get('action')
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        override = request.POST.get('override') == 'on'

        if action == 'approve':
            if provider.free_listing_credits > 0:
                provider.free_listing_credits -= 1
                provider.save()
            elif not override:
                messages.error(request, 'Kredit 0. Override belgilang.')
                return redirect('dashboard:listing_review', pk=listing.pk)

            listing.status = Listing.Status.APPROVED
            listing.is_public = True
            listing.rejection_reason = ''
            listing.save()
            messages.success(request, 'E’lon tasdiqlandi.')
            return redirect('dashboard:pending_listings')

        if action == 'reject':
            if not rejection_reason:
                messages.error(request, 'Rad sababini kiriting.')
                return redirect('dashboard:listing_review', pk=listing.pk)
            listing.status = Listing.Status.REJECTED
            listing.is_public = False
            listing.rejection_reason = rejection_reason
            listing.save()
            messages.success(request, 'E’lon rad etildi.')
            return redirect('dashboard:pending_listings')

    return render(request, 'dashboard/listing_review.html', {'listing': listing, 'provider': provider})


@user_passes_test(is_admin)
def provider_list(request):
    providers = Provider.objects.select_related('user').order_by('user__username')
    return render(request, 'dashboard/provider_list.html', {'providers': providers})

# Create your views here.
