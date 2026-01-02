from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from providers.models import Provider
from services.models import Category, Service
from .models import Listing


User = get_user_model()


class ListingApprovalTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='pass', role=User.Roles.ADMIN
        )
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.service = Service.objects.create(
            category=self.category, name='Test Service', description='Desc'
        )
        self.provider_user = User.objects.create_user(
            username='provider', password='pass', role=User.Roles.PROVIDER
        )
        self.provider = Provider.objects.create(user=self.provider_user, free_listing_credits=3)
        self.listing = Listing.objects.create(
            provider=self.provider,
            category=self.category,
            service=self.service,
            title='Test Listing',
            description='Desc',
            city='Toshkent',
            district='Markaz',
            status=Listing.Status.PENDING,
        )

    def test_approval_reduces_credits(self):
        self.client.login(username='admin', password='pass')
        url = reverse('dashboard:listing_review', args=[self.listing.pk])
        response = self.client.post(url, {'action': 'approve'})
        self.assertRedirects(response, reverse('dashboard:pending_listings'))
        self.provider.refresh_from_db()
        self.listing.refresh_from_db()
        self.assertEqual(self.provider.free_listing_credits, 2)
        self.assertEqual(self.listing.status, Listing.Status.APPROVED)
        self.assertTrue(self.listing.is_public)

    def test_listing_not_visible_until_approved(self):
        url = reverse('listings:public_list')
        response = self.client.get(url)
        self.assertNotContains(response, self.listing.title)
        self.listing.status = Listing.Status.APPROVED
        self.listing.is_public = True
        self.listing.save()
        response = self.client.get(url)
        self.assertContains(response, self.listing.title)

    def test_reject_stores_reason(self):
        self.client.login(username='admin', password='pass')
        url = reverse('dashboard:listing_review', args=[self.listing.pk])
        response = self.client.post(url, {'action': 'reject', 'rejection_reason': 'Bad info'})
        self.assertRedirects(response, reverse('dashboard:pending_listings'))
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, Listing.Status.REJECTED)
        self.assertEqual(self.listing.rejection_reason, 'Bad info')

# Create your tests here.
