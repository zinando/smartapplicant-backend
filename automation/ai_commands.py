from .models import WebhookEvent, AutomatedClients, Tenant
from .messaging import send_text_reply
from django.conf import settings

def message_admin(event:WebhookEvent, message:str, contact:str):
    send_text_reply(event, contact, message)
def register_new_page_for_content_automation(event:WebhookEvent, page_id:str, platform:str):
    """pages will be registered under AutomatedClients table using smartapplicant as the tenant"""
    try:
        phone_number_id=settings.SMARTAPPLICANT.get("PHONE_NUMBER_ID")
        if not phone_number_id:
            raise Exception("no valid waba phone number ID detected")
        default_tenant = Tenant.objects.get(waba_phone_number_id=phone_number_id)
        client, created = AutomatedClients.objects.get_or_create(
            tenant=default_tenant,
            platform=platform,
            client_id=page_id,
            defaults={
                
            }
        )
    except Exception as e:
        pass

def command_map() -> dict:
    return {
        "send_message_to_admin": message_admin,
        "send_message_to_customer": message_admin,
        "register_new_facebook_page_for_content_automation": register_new_page_for_content_automation,
    }
