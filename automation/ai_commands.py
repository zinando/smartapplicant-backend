from .models import WebhookEvent, AutomatedClients, Tenant, FacebookAuthLog
from .messaging import send_text_reply
from django.conf import settings
import json
from .mydata import business_info_form_template
from .context_manager import save_context

def message_admin(event:WebhookEvent, message:str, contact:str):
    send_text_reply(event, contact, message)
def register_new_page_for_content_automation(event:WebhookEvent, page_id:str, platform:str, session_id:str, payment_ref:str=None):
    """pages will be registered under AutomatedClients table using smartapplicant as the tenant"""
    form = ''
    try:
        if not payment_ref:
            raise Exception("payment reference is required to register a new facebook page for content automation")
        phone_number_id=settings.SMARTAPPLICANT.get("PHONE_NUMBER_ID")
        if not phone_number_id:
            raise Exception("no valid waba phone number ID detected")
        default_tenant = Tenant.objects.get(waba_phone_number_id=phone_number_id)
        auth_log = FacebookAuthLog.objects.filter(state=session_id).first()
        if not auth_log:
            raise Exception("no valid facebook page authorization log detected for the given session id")
        payload = json.loads(auth_log.page_access_token_payload)
        pages = payload['data']
        target_page = [page for page in pages if str(page['id']) == page_id]
        if not target_page:
            raise Exception("the given page id was not found in the authorized pages list")
        page_access_token = target_page[0]['access_token']
        if not page_access_token:
            raise Exception("no valid page access token found for the given page id")
        
        obj, created = AutomatedClients.objects.get_or_create(
            tenant=default_tenant,
            auth_log=auth_log,
            platform=platform,
            client_id=page_id,
            defaults={
                "page_access_token": str(page_access_token),
                "subscription_ref": payment_ref,
            },
        )
        if created:
            message = f"Facebook page with ID {page_id} has been successfully registered for content automation.\nYou are to securely keep your page ID, and reference it for future use."
            message += f"\nNext step: update your page account with information about your business by copying the form below and updating the relevant fields:\n"
            form += business_info_form_template
        else:
            message = f"Facebook page with ID {page_id} is already registered for content automation."
            if not obj.business_details:
                message += f"\nNext step: update your page account with information about your business by copying the form below and updating the relevant fields:\n"
                form += business_info_form_template
        
    except Exception as e:
        form = ''
        message = f"An error occurred while registering the Facebook page for content automation: {str(e)}"
    
    # save context 
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"
    save_context(f"Register new facebook page for content automation with page id {page_id} and platform {platform}", message, context_id)
    send_text_reply(event, event.sender_id, message)

    if form:
        save_context("Business information form for content automation", form, context_id)
        send_text_reply(event, event.sender_id, form)
    
    return

def confirm_payment(event:WebhookEvent, payment_ref:str):
    """Confirms the status of a transaction with a given reference from a customer. Result is shared in the context."""
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"
    text = f"Confirming payment with reference: {payment_ref}"
    if not payment_ref:
        message = "Payment Amount: -\n"
        message += "Status: No payment reference provided."
    else:
        message = "Payment Amount: N5000\n"
        message = "Payment Time: 2025-12-12 04:45:24\n"
        message += "Narration: 1 month subscription for Facebook page content automation\n"
        message += "Status: Successful."
    
    save_context(text, message, context_id)
    send_text_reply(event, event.sender_id, message)

def command_map() -> dict:
    return {
        "send_message_to_admin": message_admin,
        "send_message_to_customer": message_admin,
        "register_new_facebook_page_for_content_automation": register_new_page_for_content_automation,
        "confirm_payment": confirm_payment,
    }
