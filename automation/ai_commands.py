from .models import WebhookEvent
from .messaging import send_text_reply

def message_admin(event:WebhookEvent, message:str, contact:str):
    send_text_reply(event, contact, message)

def command_map() -> dict:
    return {
        "send_message_to_admin": message_admin,
        "send_message_to_customer": message_admin,
    }
