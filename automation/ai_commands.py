from .models import WebhookEvent, AutomatedClients, Tenant, FacebookAuthLog
from .messaging import send_text_reply
from django.conf import settings
import json
from django.utils import timezone
from datetime import timedelta
from .mydata import business_info_form_template, business_info
from .context_manager import save_context
from typing import List, Dict

def message_admin(event:WebhookEvent, message:str, contact:str):
    send_text_reply(event, contact, message)
def register_new_page_for_content_automation(event:WebhookEvent, page_id:str, platform:str, session_id:str, secret_questions:List[Dict[str, str]]):
    """pages will be registered under AutomatedClients table using smartapplicant as the tenant"""
    form = ''
    try:
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
                "secret_questions": secret_questions,
                # "subscription_ref": payment_ref,
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

def subscribe_to_post_automation(event: WebhookEvent, subscription_days:int, page_id, payment_ref=''):
    """Subscribes for a given number of days for the page_id"""
    allowed_number_of_days = [3, 30]
    message = ''
    try:
        if subscription_days not in allowed_number_of_days:
            raise Exception(f"{subscription_days} days is not allowed. Only {'days, '.join(allowed_number_of_days)} are allowed.")
        if not payment_ref and subscription_days > 3:
            raise Exception("Payment is required for subscriptions above the 3 day trial period.")
        client = AutomatedClients.objects.filter(client_id=page_id).first()
        client.run_subscription_expiry_check()
        if client.subscribed:
            # client has active subscription. check if it'd expeire in three days time, then top it up with current sub
            if subscription_days > 3 and (timezone.now() + timedelta(days=3)) >= client.subscription_expires_at: # if sub will expire in days time and new sub is non three day sub
                client.subscription_expires_at += timedelta(days=subscription_days)
                client.save(update_fields=["subscription_expires_at"])
                message = f'Subscription updated for client. New expiry date is now {client.subscription_expires_at.strftime("%d-%m-%Y")}.'
            else:
                raise Exception(f"Client still has active subscription that will expire on {client.subscription_expires_at.strftime('%d-%m-%Y')}.") 
        # sub for client 
        else:
            client.subscription_expires_at = timedelta(days=subscription_days)
            client.save(update_fields=['subscription_expires_at'])
            message = f'Client Subscription was successful. Subscription expiry date is {client.subscription_expires_at.strftime("%d-%m-%Y")}.'
    except Exception as e:
        message = str(e)
    
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"

    save_context("You ran this command for this user: subscribe_to_post_automation. And here is the result:", message, context_id)
    send_text_reply(event, event.sender_id, message)

def update_client_info(event:WebhookEvent, biz_info:dict, page_id):
    """Helps automated clients to update their business info"""
    try:
        client = AutomatedClients.objects.filter(client_id=page_id).first()
        client_info = client.business_details
        info = {}
        if not client_info:
            for key in business_info.keys():
                default = business_info.get(key)
                if isinstance(default, dict):
                    default_value = {}
                elif isinstance(default, list):
                    default_value = []
                elif isinstance(default, bool):
                    default_value = default
                else:
                    default_value = ''
                info[key] = biz_info.get(key, default_value)
            client.business_details = info
            client.save(update_fields=["business_details"])
            message = f"Buiness info was created successfully."
        else:
            for key in business_info.keys():
                info[key] = biz_info.get(key, client_info.get(key))
            client.business_details = info
            client.save(update_fields=["business_details"])
            message = f"Buiness info was updated successfully."

    except Exception as e:
        message = str(e)
    
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"

    save_context("You ran this command for this user: update_client_info. And here is the result:", message, context_id)
    send_text_reply(event, event.sender_id, message)
    
def command_map() -> dict:
    return {
        "send_message_to_admin": message_admin,
        "send_message_to_customer": message_admin,
        "register_new_facebook_page_for_content_automation": register_new_page_for_content_automation,
        "confirm_payment": confirm_payment,
        "subscribe_to_post_automation": subscribe_to_post_automation,
        "update_client_info": update_client_info,
    }
