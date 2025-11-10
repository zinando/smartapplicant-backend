"""Routes messages to appropriate handlers by using event object."""
import logging
from .models import WebhookEvent
import base64

logger = logging.getLogger(__name__)

def send_text_reply(event: WebhookEvent, recipient: str, reply_text: str):
    """
    Send reply based on event platform.
    """
    platform = event.platform

    if platform == "whatsapp":
        from .webhook_handlers.whatsapp import send_whatsapp_text_message
        send_whatsapp_text_message(event.tenant.waba_phone_number_id, recipient, reply_text)

    elif platform == "facebook":
        from .webhook_handlers.facebook import send_facebook_reply
        send_facebook_reply(event.sender_id, reply_text, event.tenant)

    elif platform == "instagram":
        from .webhook_handlers.instagram import send_instagram_reply
        send_instagram_reply(event.sender_id, reply_text, event.tenant)

    elif platform == "telegram":
        from .webhook_handlers.telegram import send_telegram_reply
        send_telegram_reply(event.sender_id, reply_text, event.tenant)

    else:
        logger.warning(f"Unsupported platform: {platform}")

def send_media_reply(event: WebhookEvent, recipient: str, media_content: base64, caption: str = ""):
    """
    Send media reply based on event platform.
    """
    platform = event.platform

    if platform == "whatsapp":
        from .webhook_handlers.whatsapp import send_whatsapp_media_message
        media_bytes = base64.b64decode(media_content)
        send_whatsapp_media_message(event.tenant.waba_phone_number_id, recipient, media_bytes, caption)

    elif platform == "facebook":
        from .webhook_handlers.facebook import send_facebook_media_reply
        send_facebook_media_reply(event.sender_id, media_bytes, caption, event.tenant)

    elif platform == "instagram":
        from .webhook_handlers.instagram import send_instagram_media_reply
        send_instagram_media_reply(event.sender_id, media_bytes, caption, event.tenant)

    elif platform == "telegram":
        from .webhook_handlers.telegram import send_telegram_media_reply
        send_telegram_media_reply(event.sender_id, media_bytes, caption, event.tenant)

    else:
        logger.warning(f"Unsupported platform for media: {platform}")