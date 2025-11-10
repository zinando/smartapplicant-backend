from .models import AutomatedClients, Tenant
from django.utils import timezone

def add_tenant(name, waba_id, waba_phone_number, waba_phone_number_id, business_details=None,
               fb_page_id=None, ig_business_account_id=None, tg_bot_username=None,
               custom_prompts=None, content_schedule_times=None, media_history=None,
               evergreen_content=None, customers=None):
     tenant = Tenant(
        name = name,
        waba_id = waba_id,
        waba_phone_number = waba_phone_number,
        waba_phone_number_id = waba_phone_number_id,
        fb_page_id = fb_page_id,
        ig_business_account_id = ig_business_account_id,
        tg_bot_username = tg_bot_username,
        custom_prompts = custom_prompts,
        business_details = business_details,
        content_schedule_times = content_schedule_times,
        media_history = media_history,
        evergreen_content = evergreen_content,
        customers = customers,
     )
     tenant.save()
     return tenant
def add_client(tenant, platform, client_id, access_token, token_expires_at=None,
               subscribed=False, subscription_ref=None, subscription_expires_at=None):
    client = AutomatedClients(
        tenant=tenant,
        platform=platform,
        client_id=client_id,
        access_token=access_token,
        token_expires_at=token_expires_at,
        subscribed=subscribed,
        subscription_ref=subscription_ref,
        subscription_expires_at=subscription_expires_at
    )
    client.save()
    return client

def update_client_subscription(client: AutomatedClients, subscribed: bool, subscription_expires_at=None):
    client.subscribed = subscribed
    client.subscription_expires_at = subscription_expires_at 
    client.save(update_fields=['subscribed', 'subscription_expires_at'])