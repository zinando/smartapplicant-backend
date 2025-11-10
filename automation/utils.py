from .webhook_handlers.whatsapp import parse_whatsapp_payload
from datetime import datetime, timezone
import base64

def to_facebook_timestamp(hour, minute=0):
    dt = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    dt_utc = dt.astimezone(timezone.utc)
    return int(dt_utc.timestamp())

def base64_to_bytes(base64_string: str) -> bytes | str:
    """
    Convert a base64 encoded string to bytes.
    If decoding fails, return the original string.
    """
    try:
        # If the string has a data URI scheme, strip it
        if "," in base64_string:
            base64_string = base64_string.split(",", 1)[1]

        return base64.b64decode(base64_string)
    except Exception:
        # Return the original string if it's not valid base64
        return base64_string
        
def normalize_payload(payload: dict):
    """
    Detect platform and extract sender + message.
    Returns: dict(platform, sender_id, message)
    """
    # WhatsApp
    if payload.get("object") == "whatsapp_business_account":
        return parse_whatsapp_payload(payload)
    # Facebook Page messages
    if "object" in payload and payload["object"] == "page":
        messaging = payload["entry"][0]["messaging"][0]
        return {
            "platform": "facebook",
            "sender_id": messaging["sender"]["id"],
            "message": messaging["message"].get("text", ""),
        }

    # Instagram DM
    if "object" in payload and payload["object"] == "instagram":
        messaging = payload["entry"][0]["messaging"][0]
        return {
            "platform": "instagram",
            "sender_id": messaging["sender"]["id"],
            "message": messaging["message"].get("text", ""),
        }

    # Telegram
    if "message" in payload and "chat" in payload["message"]:
        msg = payload["message"]
        return {
            "platform": "telegram",
            "sender_id": msg["chat"]["id"],
            "message": msg.get("text", ""),
        }

    return {}

