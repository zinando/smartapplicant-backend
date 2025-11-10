import requests
from django.conf import settings

def _get_auth_headers():
    """Return standard authorization headers."""
    return {
        "Authorization": f"Bearer {settings.BUSINESS_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

def _upload_media(biz_id, media_bytes, media_type="image"):
    """
    Upload media to WhatsApp Cloud API.
    Returns the media_id if successful.
    """
    url = f"{settings.META_GRAPH_URL}/{biz_id}/media"
    headers = {"Authorization": f"Bearer {settings.BUSINESS_ACCESS_TOKEN}"}
    files = {
        "file": ("media", media_bytes, media_type),
        "type": (None, media_type)
    }

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        media_id = response.json().get("id")
        return media_id
    except Exception as e:
        print(f"Error uploading media: {e}")
        return None

def _send_media_message(biz_id, to, media_id, media_type="image", caption=None):
    """Send uploaded media to a recipient."""
    url = f"{settings.META_GRAPH_URL}/{biz_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": media_type,
        media_type: {"id": media_id}
    }

    if caption:
        payload[media_type]["caption"] = caption

    try:
        response = requests.post(url, headers=_get_auth_headers(), json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending media message: {e}")
        return {"error": str(e)}

def send_whatsapp_media_message(biz_id, to, media_bytes, media_type="image", caption=''):
    """
    Upload and send a WhatsApp media message.
    """
    media_id = _upload_media(biz_id, media_bytes, media_type)
    if not media_id:
        return {"error": "Media upload failed"}
    return _send_media_message(biz_id, to, media_id, media_type, caption)

def send_whatsapp_text_message(biz_id, to, text):
    url = f"{settings.META_GRAPH_URL}/{biz_id}/messages"
    headers = _get_auth_headers()
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        return {"error": str(e)}
    
def download_whatsapp_media(media_id):
    try:
        url = f"{settings.META_GRAPH_URL}/{media_id}"
        headers = {"Authorization": f"Bearer {settings.BUSINESS_ACCESS_TOKEN}"}

        # Step 1: get media URL
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        media_url = res.json()["url"]

        # Step 2: download media content
        file_res = requests.get(media_url, headers=headers)
        file_res.raise_for_status()
        return file_res.content  # raw bytes (you can save to file or DB)
    except Exception as e:
        print(f"Error downloading media {media_id}: {e}")
        return None

def parse_whatsapp_payload(payload: dict):
    if payload.get("object") != "whatsapp_business_account":
        return {}

    entry = payload.get("entry", [])
    if not entry:
        return {}

    changes = entry[0].get("changes", [])
    if not changes:
        return {}

    value = changes[0].get("value", {})
    if not value:
        return {}

    return extract_whatsapp_data(value)

def extract_whatsapp_data(value: dict):
    metadata = value.get("metadata", {})
    contacts = value.get("contacts", [])
    messages = value.get("messages", [])

    sender_name = extract_sender_name(contacts)
    biz_id = metadata.get("phone_number_id", "Unknown")

    if not messages:
        return {}

    return extract_message_info(messages[0], sender_name, biz_id)

def extract_sender_name(contacts: list):
    if not contacts:
        return "Unknown"
    profile = contacts[0].get("profile", {})
    return profile.get("name", "Unknown")

def extract_message_info(msg: dict, sender_name: str, biz_id: str):
    msg_type = msg.get("type")
    sender_id = msg.get("from", "Unknown")

    if msg_type == "text":
        return handle_text_message(msg, sender_name, sender_id, biz_id)
    elif msg_type in ("image", "video", "audio", "document", "sticker"):
        return handle_media_message(msg, msg_type, sender_name, sender_id, biz_id)
    return {}

def handle_text_message(msg, sender_name, sender_id, biz_id):
    text = msg.get("text", {})
    if not text:
        return {}
    text_body = text.get("body", "")
    return {
        "platform": "whatsapp",
        "biz_id": biz_id,
        "sender_id": sender_id,
        "sender_name": sender_name,
        "message": text_body,
    }

def handle_media_message(msg, msg_type, sender_name, sender_id, biz_id):
    media = msg.get(msg_type, {})
    if not media:
        return {}
    media_object = download_whatsapp_media(media.get("id"))
    return {
        "platform": "whatsapp",
        "biz_id": biz_id,
        "sender_id": sender_id,
        "sender_name": sender_name,
        "message": f"{msg_type.upper()} MESSAGE",
        "media_id": media.get("id"),
        "media_type": msg_type,
        "mime_type": media.get("mime_type"),
        "caption": media.get("caption", None),
        "media_object": media_object,
    }

