from .models import AutomatedClients, Tenant
from django.utils import timezone
from .helpers import save_cache, get_cache

def save_admin_contacts_to_cache(key, value, timeout=None):
    """Saves admin contacts to cache"""
    save_cache(key, value, timeout=timeout)

def add_tenant(name, waba_id, waba_phone_number, waba_phone_number_id, business_details=None,
               fb_page_id=None, ig_business_account_id=None, tg_bot_username=None,
               custom_prompts=None, content_schedule_times=None, media_history=None,
               evergreen_content=None, customers=None):
    # tenant = Tenant(
    # name = name,
    # waba_id = waba_id,
    # waba_phone_number = waba_phone_number,
    # waba_phone_number_id = waba_phone_number_id,
    # fb_page_id = fb_page_id,
    # ig_business_account_id = ig_business_account_id,
    # tg_bot_username = tg_bot_username,
    # custom_prompts = custom_prompts,
    # business_details = business_details,
    # content_schedule_times = content_schedule_times,
    # media_history = media_history,
    # evergreen_content = evergreen_content,
    # customers = customers,
    # )
    # tenant.save()
    tenant, created = Tenant.objects.get_or_create(
        waba_phone_number_id=waba_phone_number_id,
        defaults={
            'name': name,
            'waba_id': waba_id,
            'waba_phone_number': waba_phone_number,
            'business_details': business_details,
            'fb_page_id': fb_page_id,
            'ig_business_account_id': ig_business_account_id,
            'tg_bot_username': tg_bot_username,
            'custom_prompts': custom_prompts,
            'content_schedule_times': content_schedule_times,
            'media_history': media_history,
            'evergreen_content': evergreen_content,
            'customers': customers,
        }
    )
    key = f"{tenant.waba_phone_number_id}_admin_contacts"
    biz_info = tenant.business_details or {}
    if biz_info:
        admin_contacts = [
            value for key, value in
            biz_info.get("admin_contacts", {}).items()]
        if admin_contacts:
            save_admin_contacts_to_cache(key, list(set(admin_contacts)), timeout=None)
            print(f"Saved admin contacts to cache for tenant {tenant.name}")
    return tenant

def add_client(tenant, platform, client_id, access_token, token_expires_at=None,
               subscribed=False, subscription_ref=None, subscription_expires_at=None):
    # client = AutomatedClients(
    #     tenant=tenant,
    #     platform=platform,
    #     client_id=client_id,
    #     access_token=access_token,
    #     token_expires_at=token_expires_at,
    #     subscribed=subscribed,
    #     subscription_ref=subscription_ref,
    #     subscription_expires_at=subscription_expires_at
    # )
    # client.save()
    client, created = AutomatedClients.objects.get_or_create(
        client_id=client_id,
        defaults={
            'tenant': tenant,
            'platform': platform,
            'page_access_token': access_token,
            'token_expires_at': token_expires_at,
            'subscribed': subscribed,
            'subscription_ref': subscription_ref,
            'subscription_expires_at': subscription_expires_at
        }
    )
    return client

def update_client_subscription(client: AutomatedClients, subscribed: bool, subscription_expires_at=None):
    client.subscribed = subscribed
    client.subscription_expires_at = subscription_expires_at 
    client.save(update_fields=['subscribed', 'subscription_expires_at'])

