from automation.models import Tenant
from automation.helpers import save_cache

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
