import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from automation.models import *
from django.conf import settings
from automation.mydata import tenant, business_info
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

@pytest.fixture
def app_tenant(db):
    mytenant, created = Tenant.objects.get_or_create(
        waba_phone_number_id=tenant['waba_phone_number_id'],
        defaults={
            'name': tenant['name'],
            'waba_id': tenant['waba_id'],
            'waba_phone_number': tenant['waba_phone_number'],
            'business_details': tenant['business_details'],
            'fb_page_id': tenant['fb_page_id'],
            'ig_business_account_id': tenant['ig_business_account_id'],
            'tg_bot_username': tenant['tg_bot_username'],
            'custom_prompts': tenant['custom_prompts'],
            'content_schedule_times': tenant['content_schedule_times'],
            'media_history': tenant['media_history'],
            'evergreen_content': tenant['evergreen_content'],
            'customers': tenant['customers'],
        })
    return mytenant

@pytest.fixture
def app_client(db, app_tenant):
    myclient, created = AutomatedClients.objects.get_or_create(
        client_id= app_tenant.fb_page_id,
        defaults={
            'tenant': app_tenant,
            'platform': 'facebook',
            'page_access_token': settings.PAGE_DATA.get(app_tenant.fb_page_id, {}).get('access_token'),
            'token_expires_at': settings.PAGE_DATA.get(app_tenant.fb_page_id, {}).get('token_expires_at'),
            'subscribed': True,
            'subscription_ref': 'sub_ref_123',
            'subscription_expires_at': timezone.now() + timedelta(days=3),
            'business_details': business_info,
            'media_history': app_tenant.media_history.get('facebook', []),
            'evergreen_content': app_tenant.evergreen_content,
            'content_schedule_times': app_tenant.content_schedule_times.get('facebook', []),
        }
    )
    return myclient