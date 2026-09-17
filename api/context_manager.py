from django.core.cache import cache
from django.utils import timezone
from .tasks import persist_conversation_to_db


def get_conversation_context(user_phone:str, limit:int=200)->tuple[str, dict]:
    """
    Retrieve the conversation for a given user phone number.
    context structure:
    {
        "conversation": [
            {
                "role": "",
                "message": "",
                "timestamp": ""
            }
        ],
        "state": {
            "intent": "",
            "intent_attributes": {}
        }
    }
    """
    
    key = f"conversation_{user_phone}"
    context = cache.get(key) or {}
    if not context:
        return '', {}
    
    conversation = context.get('conversation') or []
    conversation_state = context.get('state') or {}

    conversation_text = ""
    for message in conversation[-limit:]:  # Get the last 'limit' messages
        role = message['role']
        text = message['message']
        timestamp = message['timestamp']
        conversation_text += f"{role.capitalize()} said: {text} ---{timestamp}\n\n"

    return conversation_text, conversation_state

def set_conversation_context(user_phone:str, role:str, message:str, structured_json_state:dict=None, ttl:int=None):
    """
    Save the conversation for a given user phone number.
    context structure:
    {
        "conversation": [
            {
                "role": "",
                "message": "",
                "timestamp": ""
            }
        ],
        "state": {
            "intent": "",
            "intent_attributes": {}
        }
    }
    """
    # 7days ttl
    ttl = ttl or 7 * 24 * 60 * 60
    key = f"conversation_{user_phone}"
    context = cache.get(key) or {}
    
    # Update conversation
    conversation = context.get('conversation') or []
    convo = {
        'role': role,
        'message': message,
        'timestamp': timezone.now().isoformat()
    }
    conversation.append(convo)
    
    # Update state if provided
    if structured_json_state is not None:
        context['state'] = structured_json_state
    
    context['conversation'] = conversation
    cache.set(key, context, timeout=ttl)

    # Persist conversation to database
    persist_conversation_to_db.delay(user_phone, convo, structured_json_state)

