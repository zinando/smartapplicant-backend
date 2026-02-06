from celery import shared_task
import logging
from .utils import (normalize_payload, to_facebook_timestamp, base64_to_bytes, 
                    get_random_admin_instant_message, is_url)
from .models import WebhookEvent, Tenant, AutomatedClients, MediaPostLog
from .mydata import business_info
from .helpers import *
from .admin_commands import process_admin_command
from .admin_reply import process_admin_message
from .customer_reply import process_customer_message
from .messaging import send_text_reply, send_media_reply
from api.ai import get_image_from_grok, get_structured_data_from_gemini_smart
from .context_manager import save_context
from .content_automation.facebook import AutomateFacebookPost
from .content_automation.post_video import FacebookVideoUploader
from .video_generator import VideoGenerator
import time
from django.utils import timezone
from datetime import timedelta
import re
from django.db import transaction
from .ai_commands import command_map as customer_command_map


logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def handle_inbound_event(self, payload):
    # logger.info("Processing inbound event: %s", payload)
    # Normalize
    normalized = normalize_payload(payload)
    platform = normalized.get("platform")
    sender_id = normalized.get("sender_id")
    message = normalized.get("message")
    business_id = normalized.get("biz_id")

    # Find tenant by business_id (phone_number_id)
    tenant = Tenant.objects.filter(waba_phone_number_id=business_id).first()

    if tenant:
        # Save raw event
        event = WebhookEvent.objects.create(
            tenant=tenant,
            platform=platform,
            sender_id=sender_id,
            sender_name=normalized.get("sender_name"),
            message=message,
            raw=payload,
            media_id = normalized.get("media_id"),
            media_type = normalized.get("media_type"),
            mime_type = normalized.get("mime_type"),
            caption = normalized.get("caption"),
        )

        # Add to customers list if new
        if sender_id not in tenant.customers:
            tenant.customers.append(sender_id)
            tenant.save(update_fields=["customers"])

        # Enqueue next step (AI or auto reply)
        trigger_message_processing.delay(event.id)
        return f"Event {event.id} processed"
    else:
        logger.warning("No tenant found for business_id: %s", business_id)
        self.retry(exc=Exception("Tenant not found"), countdown=1)
    
@shared_task(bind=True, max_retries=3)
def trigger_message_processing(self, event_id):
    """
    Processes message and generates AI prompt based on message type and sender.
    """
    try:
        event = WebhookEvent.objects.get(id=event_id)
        admin_contacts_key = f"{event.tenant.waba_phone_number_id}_admin_contacts"
        admin_contacts = get_cache(admin_contacts_key) or []

        print(f"admin contacts {admin_contacts}")

        # check for admin messages
        if event.message.startswith("##") and event.sender_id in admin_contacts:
            acknowledge = get_random_admin_instant_message()
            send_text_reply(event, event.sender_id, acknowledge)

            # process admin command
            logger.info(f"Admin message detected in event {event_id}, skipping auto-reply.")
            command_text = re.search(r"##(.*)", event.message).group(1)
            result = process_admin_command(command_text, event)
            if isinstance(result, str):
                send_text_reply(event, event.sender_id, result)
            elif isinstance(result, list):
                for res in result:
                    time.sleep(2)  # brief pause between messages
                    send_text_reply(event, event.sender_id, res)
            return
        
        elif event.sender_id in admin_contacts:
            # process admin response to customer enquiry
            # print("processing admin message")
            prompt = process_admin_message(event)
            generate_ai_response.delay(event.id, prompt)
            return
        
        # process normal client message
        prompt = process_customer_message(event)

        generate_ai_response.delay(event.id, prompt)

        event.processed = True
        event.save(update_fields=["processed"])
    except Exception as e:
        logger.error(f"Error processing event {event_id}: {e}")
        send_text_reply(event, event.sender_id, f"Sorry, an error occurred while processing your message: {e}")
        # self.retry(exc=e, countdown=3)

@shared_task(bind=True, max_retries=3)
def generate_ai_response(self, event_id: int, prompt: str):
    """
    Generates AI response unsing the given prompt.
    Sends the AI-generated reply back to the customer.
    Schedules other tasks as needed based on AI response.
    Retries up to 3 times on failure. 
    """
    event = WebhookEvent.objects.get(id=event_id)
    try:
        logger.info(f"Generating AI response for event {event.id}")
        ai_response = get_structured_data_from_gemini_smart(prompt)
        print(f"AI Response: {ai_response}")

        context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"

        # Send reply based on AI response
        if ai_response.get("status") == 1:
            # Normal reply to customer: handle text or media
            if ai_response.get("type") == "media":
                media_info = ai_response.get("message", {})

                # save context
                save_context(
                    text=event.message,
                    response=media_info.get("media", ""),
                    context_id=context_id
                )
                
                send_media_reply(
                    event,
                    event.sender_id,
                    media_type=media_info.get("media_type"),
                    media_content=media_info.get("media"),
                    caption=media_info.get("caption", "")
                )
                return
            # elif isinstance(ai_response.get("message"), dict):
            #     ai_message = ai_response.get("message")
            #     if "admin" in ai_message and isinstance(ai_message.get("admin"), dict):
                    
            message = ai_response.get("message", "Thank you for your message.")
            # save context
            save_context(
                text=event.message,
                response=message,
                context_id=context_id
            )
            send_text_reply(event,event.sender_id, message)
        elif ai_response.get("status") == 0:
            # Needs admin attention
            details = ai_response.get("message", {})
            actions = ai_response.get("actions", [])
            if "admin" in details and "customers" in details:
                """This is response addressing constomer enquiries using admin input"""
                # send_text_reply(event, event.sender_id, "message structure is good" )
                admin_message = details.get("admin", {})
                customers = details.get("customers", [])
                if admin_message:
                    # send_text_reply(event, event.sender_id, "there is message for admin" )
                    # print("there is a message for admin")
                    admin_contact = admin_message.get("admin_contact")
                    reply_to_admin = admin_message.get("response")

                    send_text_reply(event, admin_contact, reply_to_admin)
                    # save context for admin
                    save_context(
                        text='(You messaged this admin)',
                        response=f'YOUR MESSAGE:\n{reply_to_admin}',
                        context_id=f"{event.tenant.waba_phone_number_id}_{admin_contact}"
                    )

                if customers:
                    # print("There are messages for customers")
                    # send_text_reply(event, event.sender_id, f"{customer}" )
                    # address all the customer enquiry
                    for customer in customers:
                        save_context(
                            text=' ',
                            response=customer.get("response"),
                            context_id=f"{event.tenant.waba_phone_number_id}_{customer.get('to')}"
                        )
                        send_text_reply(event, customer.get('to'), f'{customer.get("response")}- {customer.get("event_id")}')

                        # remove item from pending request
                        request_key = f"{event.tenant.waba_phone_number_id}_{admin_contact}_pending_requests"
                        remove_pending_request(request_key, customer.get("event_id"))
                
                if actions and isinstance(actions, list):
                    for action in actions:
                        command = action.get("command")
                        params = action.get("params", {})
                        
                        try:
                            map = customer_command_map()
                            func = map.get(command)
                            func(event, **params)
                            
                        except Exception as e:
                            # Save context for customer
                            save_context(
                                text=event.message,
                                response=f"Sorry i could not carry out this action: {command}",
                                context_id=f"{event.tenant.waba_phone_number_id}_{event.sender_id}"
                            )
                            
                            # Notify sender
                            send_text_reply(event, event.sender_id, f"Sorry i could not carry out this action: {command} due to \n{e}. Let me know if there is anything else i could do for you.")
        
                return
            
            else:
                admin_contact = details.get("admin_contact")
                request = details.get("request")
                reply_to_admin = details.get("reply_to_admin", f"Customer needs assistance on this enquiry: {event.message}.")
                reply_to_customer = details.get("reply_to_customer", "Your request is being forwarded to our team.")
                to = details.get("to", event.sender_id)

            # Send message to admin
            if admin_contact:
                send_text_reply(event, admin_contact, reply_to_admin)
                # save context for admin
                save_context(
                    text='(You messaged this admin)',
                    response=f'YOUR MESSAGE:\n{reply_to_admin}',
                    context_id=f"{event.tenant.waba_phone_number_id}_{admin_contact}"
                )

                # log pending request
                request_key = f"{event.tenant.waba_phone_number_id}_{admin_contact}_pending_requests"
                pending_request = {
                    'event_id': event.id,
                    'customer_id': to,
                    'request': request,
                    'admin_contact': admin_contact
                }
                log_pending_request(request_key, pending_request)
            
            # Save context for customer
            save_context(
                text=event.message,
                response=reply_to_customer,
                context_id=context_id
            )
            
            # Notify customer
            send_text_reply(event, to, reply_to_customer)
            return
        elif ai_response.get("reply") and "actions" in ai_response:
            """This is the reply-actions format"""
            reply = ai_response.get("reply", {})
            actions = ai_response.get("actions", [])
            if reply:
                reply_to_customer = reply.get("message", "We are processing your message.")
                to = reply.get("to", event.sender_id)

                # Save context for customer
                save_context(
                    text=event.message,
                    response=reply_to_customer,
                    context_id=context_id
                )
                
                # Notify customer
                send_text_reply(event, to, reply_to_customer)

                if actions and isinstance(actions, list):
                    for action in actions:
                        command = action.get("command")
                        params = action.get("params", {})
                        
                        try:
                            map = customer_command_map()
                            func = map.get(command)
                            func(event, **params)
                            # save context for each action item
                            save_context(
                                text='(You messaged this contact)',
                                response=f'YOUR MESSAGE:\n{params.get("message")}',
                                context_id=f"{event.tenant.waba_phone_number_id}_{params.get('contact')}"
                            )

                            if action.get("fya"):
                                # log pending request
                                request_key = f"{event.tenant.waba_phone_number_id}_{params.get('contact')}_pending_requests"
                                pending_request = {
                                    'event_id': event.id,
                                    'customer_id': to,
                                    'request': event.message,
                                    'admin_contact': params.get('contact')
                                }
                                log_pending_request(request_key, pending_request)
                        except Exception as e:
                            # Save context for customer
                            save_context(
                                text=event.message,
                                response=f"Sorry i could not carry out this action: {command}",
                                context_id=context_id
                            )
                            
                            # Notify customer
                            send_text_reply(event, to, f"Sorry i could not carry out this action: {command} due to \n{e}. Let me know if there is anything else i could do for you.")
        
                return

        else:
            logger.warning(f"Unrecognized AI response status for event {event.id}: {ai_response}")
    except Exception as e:
        logger.error(f"Error in auto-reply for event {event.id}: {e}")
        raise self.retry(exc=e, countdown=5)

@shared_task(bind=True, max_retries=3)
def schedule_facebook_post(self):
    clients = AutomatedClients.objects.all().filter(subscribed=True)
    # facebook_pages = ['750798604776594']
    if not clients or len(clients) == 0:
        logger.warning("No subscribed Facebook clients found for scheduling posts.")
        return
    facebook_pages = [client.client_id for client in clients if client.platform == 'facebook']
    
    if facebook_pages:
        for page in facebook_pages:
            client = clients.filter(client_id=page).first()
            media_post_log_obj, media_post_log_created = MediaPostLog.objects.get_or_create(
                client = client,
                defaults={
                    "image_count": 0,
                    "video_count": 0,
                    "last_image_posted_at": timezone.now() - timedelta(days=1),
                    "last_video_posted_at": timezone.now() - timedelta(days=1)
                }
            )
            tenant = client.tenant
            if tenant:
                logger.info("tenant found")
                if client.content_schedule_times and not isinstance(client.content_schedule_times, list):
                    logger.info("about to update saved contents")
                    if tenant.content_schedule_times and isinstance(tenant.content_schedule_times, dict):
                        logger.info("Updating saved contents")
                        client.content_schedule_times = tenant.content_schedule_times.get('facebook', [])
                        client.save(update_fields=['content_schedule_times'])
                if client.media_history and not isinstance(client.media_history, list):
                    if tenant.media_history and isinstance(tenant.media_history, dict):
                        client.media_history = tenant.media_history.get('facebook', [])
                        client.save(update_fields=['media_history'])
                if client.evergreen_content and not isinstance(client.evergreen_content, list):
                    if tenant.evergreen_content and isinstance(tenant.evergreen_content, list):
                        client.evergreen_content = tenant.evergreen_content
                        client.save(update_fields=['evergreen_content'])
                # if client.custom_prompt and not isinstance(client.custom_prompt, str):
                #     if tenant.custom_prompts and isinstance(tenant.custom_prompts, dict):
                #         client.custom_prompt = tenant.custom_prompts.get('facebook', '')
                #         client.save(update_fields=['custom_prompt'])
            count = 0
            try:
                instance = AutomateFacebookPost(page)
                prompt = instance.get_content_prompt()
                contents = client.saved_content or get_structured_data_from_gemini_smart(prompt)  # get content that failed to post or generate new one
                logger.info(f"Gemini contents:\n{contents}")
                if not contents or len(contents) == 0:
                    logger.warning(f"No content generated for Facebook page {page}")
                    # get fallback content 
                    contents = instance.get_fallback_posts()
                    # logger.warning(f"Fallback content {contents}")
                    if not contents or len(contents) < 6:
                        logger.error(f"No fallback content available for Facebook page {page}, skipping.")
                        continue
                image_contents = [x for x in contents if x.get('content_type') == 'image']
                
                if len(image_contents) > 0:
                    if  not media_post_log_obj.has_posted_image_today():
                        for item in image_contents:
                            if not isinstance(item['content'], (bytes, bytearray)) and not is_url(item['content']):
                                image_prompt = item.get('content')
                                image_data = get_image_from_grok(image_prompt)
                                if image_data:
                                    count += 1
                                    item['content'] = image_data['image']
                                    item['prompt'] = image_data.get('description', '')
                                    media_post_log_obj.last_image_posted_at = timezone.now()
                                    logger.info(f"Image generated: {image_data}")
                                else:
                                    logger.warning(f"Image generation failed for prompt: {image_prompt}, removing item.")
                                    contents.remove(item)
                            else:
                                logger.warning(f"We got content from saved_contents")
            except Exception as e:
                logger.error(str(e))
            finally:
                # temporarily save the final content 
                media_post_log_obj.image_count = count
                media_post_log_obj.save()
                
                if contents:
                    client.saved_content = contents
                    client.save(update_fields=["saved_content"])
                    transaction.on_commit(lambda: make_facebook_posts.delay(page))

                # create video post here if business subscribed for video content also
                if "vid" in client.subscription_type.lower():
                    create_video_content.delay(page)

@shared_task(bind=True, max_retries=3)
def make_facebook_posts(self, page_id):
    """ Schedules Facebook posts based on provided contents and post times. """
    instance = AutomateFacebookPost(page_id)
    schedule_times = instance.get_schedule_times()
    client = AutomatedClients.objects.filter(client_id=page_id).first()
    contents = client.saved_content
    errors = []
    logger.info(f"Scheduling posts for Facebook page {page_id} at times: {schedule_times} with contents:\n{contents}")
    return
    for x in range(len(contents)):
        content = contents[x]
        schedule_time = schedule_times[x % len(schedule_times)]
        
        result = instance.post_content(
            # content= base64_to_bytes(content['content']) if content.get('content_type') == 'image' else content['content'],
            content= content['content'],
            caption=content['caption'],
            content_type=content.get('content_type'),
            publish_now= False,
            comments=content.get("comments", []),
            scheduled_time=to_facebook_timestamp(schedule_time)
        )
        # logger.info(f"Post result data: {result}")
        if isinstance(result, dict) and "error" in result.keys():
            errors.append(result)
        # logger.info(f"Scheduled post result for Facebook page {page_id}: {result}")
        time.sleep(0.25)  # brief pause between posts for 2 seconds
    
    # delete saved_content from client if not all content returned error
    # logger.info(f"Errors encountered: {errors}")
    if len(errors) != len(contents):
        
        if client:
            client.saved_content = []
            client.save(update_fields=["saved_content"])
            logger.info(f"Some contents were posted...")
    
    try:
        # send email notification concerning the errors 
        if len(errors) > 0:
            message = f'The following errors were encountered while scheduling posts on your page ({instance.page_name()}):\n{errors}'
        else:
            message = f"Today's post schedule on your page ({instance.page_name()}) was successful."
        
        email = instance.page_email()
        instance.send_email(message, email)
    except Exception as e:
        instance.send_email(str(e), 'zinando2000@gmail.com')


@shared_task(bind=True, max_retrie=2)
def create_video_content(self, page_id:str, video_plan:dict=None):
    generator = VideoGenerator(page_id, video_plan)
    output_path, message = generator.render()

    post_video_content_to_facebook.delay(page_id)

@shared_task(bind=True, max_retrie=2)
def post_video_content_to_facebook(self, page_id:str):
    uploader = FacebookVideoUploader(page_id)
    result = uploader.upload()


@shared_task(bind=True, max_retries=3)
def test_beat_task():
    logger.info(f"✅ Test task executed at {timezone.now()}")

