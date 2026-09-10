from .models import WebhookEvent, AutomatedClients, Tenant, FacebookAuthLog
from .messaging import send_text_reply
from django.conf import settings
import json
from django.utils import timezone
from datetime import timedelta
from .mydata import business_info_form_template, business_info
from .context_manager import save_context
from .helpers import remove_pending_request

def add_new_client(page_id: str, platform: str, session_id: str, secret_questions: str):
    """Adds new client to database/automatedclients."""

    form = ""

    try:
        # ============================================================
        # 1. Get default tenant
        # ============================================================

        phone_number_id = settings.SMARTAPPLICANT.get(
            "PHONE_NUMBER_ID"
        )

        if not phone_number_id:
            raise Exception(
                "No valid WABA phone number ID detected."
            )

        default_tenant = Tenant.objects.get(
            waba_phone_number_id=phone_number_id
        )

        # ============================================================
        # 2. Get Facebook authorization log
        # ============================================================

        auth_log = (
            FacebookAuthLog.objects
            .filter(state=session_id)
            .first()
        )

        if not auth_log:
            raise Exception(
                "No valid Facebook page authorization log "
                "detected for the given session ID."
            )

        # ============================================================
        # 3. Safely decode page authorization payload
        # ============================================================

        payload = {}

        if auth_log.page_access_token_payload:
            try:
                payload = json.loads(
                    auth_log.page_access_token_payload
                )
            except (json.JSONDecodeError, TypeError, ValueError):
                raise Exception(
                    "Invalid page access payload stored in "
                    "Facebook authorization log."
                )

        if not isinstance(payload, dict) or not payload:
            raise Exception(
                "No page access payload data found."
            )

        # ============================================================
        # 4. Find the selected page
        #
        # facebook_select_page() now stores:
        #
        # "selected_pages": {
        #     "PAGE_ID_1": {...},
        #     "PAGE_ID_2": {...},
        #     "PAGE_ID_3": {...}
        # }
        # ============================================================

        selected_pages = payload.get(
            "selected_pages",
            {}
        )

        if not isinstance(selected_pages, dict):
            raise Exception(
                "Invalid selected pages data."
            )

        # Page IDs are stored as dictionary keys, therefore
        # normalize the incoming page_id to string.
        target_page = selected_pages.get(
            str(page_id)
        )

        if not target_page:
            raise Exception(
                f"The given page ID {page_id} was not found "
                f"in the selected pages for this session."
            )

        if not isinstance(target_page, dict):
            raise Exception(
                f"Invalid data stored for page ID {page_id}."
            )

        # ============================================================
        # 5. Get Page Access Token
        # ============================================================

        page_access_token = target_page.get(
            "access_token"
        )

        if not page_access_token:
            raise Exception(
                f"No valid page access token found for "
                f"page ID {page_id}."
            )

        # ============================================================
        # 6. Create/update AutomatedClients record
        # ============================================================

        obj, created = AutomatedClients.objects.update_or_create(
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

        # ============================================================
        # 7. Prepare response message
        # ============================================================

        if created:
            message = (
                f"Facebook page with ID {page_id} has been "
                f"successfully registered for content automation.\n"
                f"You are to securely keep your page ID, and "
                f"reference it for future use."
            )

            message += (
                "\nNext step: update your page account with "
                "information about your business by copying the "
                "form below and updating the relevant fields:\n"
            )

            form += business_info_form_template

        else:
            message = (
                f"Facebook page with ID {page_id} is already "
                f"registered for content automation."
            )

            if not obj.business_details:
                message += (
                    "\nNext step: update your page account with "
                    "information about your business by copying "
                    "the form below and updating the relevant "
                    "fields:\n"
                )

                form += business_info_form_template

        return {
            "success": True,
            "created": created,
            "message": message,
            "form": form,
            "client": obj,
        }

    except Tenant.DoesNotExist:
        return {
            "success": False,
            "message": "No tenant found for the configured WABA phone number.",
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
        }



def add_new_clientxxx(page_id:str, platform:str, session_id:str, secret_questions:str):
    """Adds new client to database/automatedclients"""
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
        if not payload:
            raise Exception("No page access payload data found.")
        target_page = payload.get("selected_page_data_payload", {})
        if not target_page or target_page.get('id') != page_id:
            raise Exception("the given page id was not found in the authorized pages list")
        page_access_token = target_page.get('access_token','')
        if not page_access_token:
            raise Exception("no valid page access token found for the given page id")
        
        obj, created = AutomatedClients.objects.update_or_create(
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
    return message, form

def message_admin(event:WebhookEvent, message:str, contact:str):
    send_text_reply(event, contact, message)

def register_new_page_for_content_automation(event:WebhookEvent, page_id:str, platform:str, session_id:str, secret_questions:str):
    """pages will be registered under AutomatedClients table using smartapplicant as the tenant"""
    message, form = add_new_client(
        page_id=page_id,
        platform=platform,
        session_id=session_id,
        secret_questions=secret_questions
    )
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
    amount = 0
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"
    text = f"Confirming payment with reference: {payment_ref}"
    if not payment_ref:
        message = "Payment Amount: -\n"
        message += "Status: No payment reference provided."
    else:
        amount = 10000
        message = f"Payment Amount: N{amount}\n"
        message += f"Payment Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += "Narration: 1 month subscription for Facebook page content automation\n"
        message += "Status: Successful."
    
    save_context(text, message, context_id)
    send_text_reply(event, event.sender_id, message)

    return amount

def get_subscription_type(amount):
    """Returns the subscription type based on payment amount"""
    sub_types = ["txt", "txt-img", "txt-img-vid", "img-vid", "txt-vid"]
    for x in sub_types:
        price = settings.SMARTAPPLICANT['PAGE_AUTOMATION_PRICES'].get(x)
        if price and int(amount) == price:
            return x
    return 'txt'  # default

def subscribe(subscription_days:int, page_id, amount:int=0, method:str='auto'):
    """Subscribes for a given number of days for the page_id"""
    if subscription_days > 3 and method == 'auto':
        return "Please contact admin for your monthly subscription. Ask the AI agent to give you admin contact. Thank you."
    allowed_number_of_days = [3, 30]
    message = ''
    subscription_type = get_subscription_type(amount)
    try:
        if subscription_days not in allowed_number_of_days:
            raise Exception(f"{subscription_days} days is not allowed. Only {', '.join(map(str, allowed_number_of_days))} day numbers are allowed.")
        if amount == 0 and subscription_days > 3:
            raise Exception("Payment is required for subscriptions above the 3 day trial period.")
        
        client = AutomatedClients.objects.filter(client_id=page_id).first()
        if not client:
            raise Exception(f"Client with ID {page_id} not found.")
        
        # check if client has business details
        if not client.business_details:
            raise Exception("Client must update business information before subscribing to a plan.")
        
        client.run_subscription_expiry_check()
        if client.subscribed:
            # client has active subscription. check if it'd expire in three days time, then top it up with current sub
            if subscription_days > 3 and (timezone.now() + timedelta(days=3)) >= client.subscription_expires_at: # if sub will expire in days time and new sub is non three day sub
                client.subscription_expires_at += timedelta(days=subscription_days)
                client.subscription_type = subscription_type
                client.save(update_fields=["subscription_expires_at", "subscription_type"])
                message = f'Subscription updated for client. New expiry date is now {client.subscription_expires_at.strftime("%d-%m-%Y")}.'
            else:
                raise Exception(f"Client still has active subscription that will expire on {client.subscription_expires_at.strftime('%d-%m-%Y')}.") 
        # sub for client 
        else:
            client.subscribed = True
            client.subscription_type = subscription_type
            client.subscription_expires_at = timezone.now() + timedelta(days=subscription_days)
            client.save(update_fields=['subscription_expires_at', 'subscription_type', 'subscribed'])
            message = f'Client Subscription was successful. Subscription expiry date is {client.subscription_expires_at.strftime("%d-%m-%Y")}.'
    except Exception as e:
        message = str(e)

    return message   

def subscribe_to_post_automation(event: WebhookEvent, subscription_days:int, page_id, payment_ref=''):
    """Subscribes for a given number of days for the page_id"""
    if payment_ref:
        amount_paid = confirm_payment(event, payment_ref)
    else:
        amount_paid = 0

    message = subscribe(
        page_id=page_id,
        subscription_days=subscription_days,
        amount=amount_paid
    )
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"

    save_context("You ran this command for this user: subscribe_to_post_automation. And here is the result:", message, context_id)
    send_text_reply(event, event.sender_id, message)

def update_info_for_client(biz_info:dict, page_id:str):
    """Helps automated clients to update their business info"""
    message = ''
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
            # subscribe for the page
            sub_message = subscribe(
                page_id=page_id,
                subscription_days=3,
                amount=0
            )
            client.save(update_fields=["business_details"])
            message = f"Buiness info was created successfully.\n{sub_message}"
        else:
            for key in business_info.keys():
                info[key] = biz_info.get(key, client_info.get(key))
            client.business_details = info
            client.save(update_fields=["business_details"])
            message = f"Buiness info was updated successfully."

    except Exception as e:
        message = str(e)
    return message

def update_client_info(event:WebhookEvent, biz_info:dict, page_id:str):
    """Helps automated clients to update their business info"""
    message = update_info_for_client(
        biz_info=biz_info,
        page_id=page_id
    )
    
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"

    save_context("You ran this command for this user: update_client_info. And here is the result:", message, context_id)
    send_text_reply(event, event.sender_id, message)

def get_secret_questions_for_client(event:WebhookEvent, page_id:str):
    """Retrieves secret questions for a given client page_id"""
    try:
        client = AutomatedClients.objects.filter(client_id=page_id).first()
        if not client:
            raise Exception(f"Client with ID {page_id} not found.")
        message = f"Secret Questions for page ID {page_id}:\n{client.secret_questions}"
    except Exception as e:
        message = str(e)

    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"

    save_context("You ran this command for this user: get_secret_questions_for_client. And here is the result:", message, context_id)

def update_secret_questions(page_id:str, secret_questions:str):
    """Updates secret questions for a given client page_id"""
    try:
        client = AutomatedClients.objects.filter(client_id=page_id).first()
        if not client:
            raise Exception(f"Client with ID {page_id} not found.")
        client.secret_questions = secret_questions
        client.save(update_fields=["secret_questions"])
        message = f"Secret Questions for page ID {page_id} have been updated successfully."
    except Exception as e:
        message = str(e)
    return message

def update_secret_questions_for_client(event:WebhookEvent, page_id:str, secret_questions:str):
    message = update_secret_questions(
        page_id=page_id,
        secret_questions=secret_questions
    )
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"

    save_context("You ran this command for this user: update_secret_questions_for_client. And here is the result:", message, context_id)
    send_text_reply(event, event.sender_id, message)
    
def get_subscription_expiry(page_id:str):
    """Checks and returns subscription expiry status for a given client page_id"""
    message = ''
    try:
        client = AutomatedClients.objects.filter(client_id=page_id).first()
        if not client:
            raise Exception(f"Client with ID {page_id} not found.")
        client.run_subscription_expiry_check()
        if client.subscribed:
            message = f"Client with ID {page_id} has an active subscription that will expire on {client.subscription_expires_at.strftime('%d-%m-%Y')}. You can extend your subscription when it is 3 days or less to the expiry date to avoid service interruption."
        else:
            if client.subscription_expires_at:
                message = f"Client with ID {page_id} had a subscription that expired on {client.subscription_expires_at.strftime('%d-%m-%Y')}."
            else:
                message = f"Client with ID {page_id} has never been subscribed. You can enjoy a 3-day trial period upon request."
    except Exception as e:
        message = str(e)
    return message

def check_subscription_expiry(event:WebhookEvent, page_id:str):
    """Checks and returns subscription expiry status for a given client page_id"""
    message = get_subscription_expiry(page_id=page_id)
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"

    save_context("You ran this command for this user: check_subscription_expiry. And here is the result:", message, context_id)
    send_text_reply(event, event.sender_id, message)

def close_pending_requests(event:WebhookEvent, request_ids:list):
    """Closes pending requests that have been fully addressed by the business admin"""
    message = ''
    try:
        if not request_ids:
            raise Exception("No request IDs provided.")
        request_key = f"{event.tenant.waba_phone_number_id}_{event.sender_id}_pending_requests"
        for id in request_ids:
            result = remove_pending_request(request_key, id)
            if result:
                message += f"{result}\n"
    except Exception as e:
        message = str(e)
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"
    save_context("You ran this command for this user: close_pending_requests. And here is the result:", message, context_id)
    send_text_reply(event, event.sender_id, message)

def update_content_schedule_times(event:WebhookEvent, page_id:str, schedule_times:list[int]):
    """Updates content schedule times for a given client page_id"""
    message = ''
    try:
        client = AutomatedClients.objects.filter(client_id=page_id).first()
        if not client:
            raise Exception(f"Client with ID {page_id} not found.")
        client.content_schedule_times = schedule_times
        client.save(update_fields=["content_schedule_times"])
        message = f"Content schedule times for page ID {page_id} have been updated successfully."
    except Exception as e:
        message = str(e)
    
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"
    save_context("You ran this command for this user: update_content_schedule_times. And here is the result:", message, context_id)
    send_text_reply(event, event.sender_id, message)    

def add_asset(page_id:str, asset:list):
    """Adds business asset(s) to the client business assets list"""
    message = ''
    try:
        client = AutomatedClients.objects.filter(client_id=page_id).first()
        if not client:
            raise Exception(f"Client with ID {page_id} not found.")
        assets = client.business_assets or []
        for a in asset:
            if a not in assets:
                assets.append(a)
        client.business_assets = assets
        client.save(update_fields=["business_assets"])
        message = f"Business asset(s) have been added successfully for page ID {page_id}."
    except Exception as e:
        message = str(e)
    return message

def add_assets_for_client(event:WebhookEvent, page_id:str, assets:list):
    """Adds business asset(s) to the client business assets list"""
    message = add_asset(
        page_id=page_id,
        asset=assets
    )
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"

    save_context("You ran this command for this user: add_assets_for_client. And here is the result:", message, context_id)
    send_text_reply(event, event.sender_id, message)

def remove_assets(page_id:str, asset:list):
    """Removes business asset(s) from the client business assets list using the asset urls"""
    message = ''
    try:
        client = AutomatedClients.objects.filter(client_id=page_id).first()
        if not client:
            raise Exception(f"Client with ID {page_id} not found.")
        assets = client.business_assets or []
        for a in asset:
            target_asset = [x for x in assets if a in x]
            if target_asset:
                assets.remove(target_asset[0])
                message += f"Asset {a} has been removed successfully for page ID {page_id}.\n"
                break
            else:
                message += f"Asset {a} not found in business assets list for page ID {page_id}.\n"
        client.business_assets = assets
        client.save(update_fields=["business_assets"])
    except Exception as e:
        message = str(e)
    return message

def remove_assets_for_client(event:WebhookEvent, page_id:str, assets:list):
    """Removes business asset(s) from the client business assets list using the asset urls"""
    message = remove_assets(
        page_id=page_id,
        asset=assets
    )
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"

    save_context("You ran this command for this user: remove_assets_for_client. And here is the result:", message, context_id)
    send_text_reply(event, event.sender_id, message)

def command_map() -> dict:
    return {
        "send_message_to_admin": message_admin,
        "send_message_to_customer": message_admin,
        "register_new_facebook_page_for_content_automation": register_new_page_for_content_automation,
        "confirm_payment": confirm_payment,
        "subscribe_to_post_automation": subscribe_to_post_automation,
        "update_client_info": update_client_info,
        "get_secret_questions_for_client": get_secret_questions_for_client,
        "update_secret_questions_for_client": update_secret_questions_for_client,
        "check_subscription_expiry": check_subscription_expiry,
        "close_pending_requests": close_pending_requests,
        "update_content_schedule_times": update_content_schedule_times,
        "add_assets_for_client": add_assets_for_client,
        "remove_assets_for_client": remove_assets_for_client,
    }
