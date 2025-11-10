from .models import WebhookEvent
from .prompts import *


def process_customer_message(event: WebhookEvent):
    """
    Process customer messages that are not from admins.
    Example scenarios:
    - Customer inquiries
    - Customer feedback
    
    route message to AI to get response
    Rule:   1. Every message always gets a reply
            2. A reply can have an accompanying action"
            3. For a customer, action can be: #to get admin response, #to place order etc
    """
    return compose_customer_text_reply_prompt(event)
    