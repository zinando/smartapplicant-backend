from .webhook_handlers.whatsapp import parse_whatsapp_payload
from datetime import datetime, timezone
import base64
import binascii
import random
from urllib.parse import urlparse

def to_facebook_timestamp(hour, minute=0):
    dt = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    dt_utc = dt.astimezone(timezone.utc)
    return int(dt_utc.timestamp())
    
def base64_to_bytes(b64: str) -> bytes:
    if "," in b64:
        b64 = b64.split(",", 1)[1]

    b64 = b64.strip().replace("\n", "").replace(" ", "")

    # Fix missing padding
    padding = len(b64) % 4
    if padding:
        b64 += "=" * (4 - padding)

    try:
        print("decoding base64 obj")
        return base64.b64decode(b64, validate=False)
    except binascii.Error as e:
        print("failed to decode base64 object")
        raise ValueError("Invalid base64 image") from e
            
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

def get_random_admin_instant_message() -> str:
    messages = [
        "On it ...",
        "Right away!",
        "Consider it done!",
        "Okay! Just a moment...",
        "I'll get that for you right away.",
        "Sure thing! Working on it now.",
        "Absolutely! Just a moment...",
    ]
    return random.choice(messages)

def is_url(value: str) -> bool:
    try:
        result = urlparse(value)
        return all([result.scheme, result.netloc])
    except:
        return False
