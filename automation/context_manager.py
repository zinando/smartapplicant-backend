from django.core.cache import cache
from django.utils import timezone

def save_context(text: str, response: str, context_id: str):
    """Save context to a file as json. Context is a dictionary with context_id as key and a list of conversations as value."""
    mr ={}
    mr['User'] = text
    mr['Response'] = response
    mr['timestamp'] = timezone.now().isoformat()
    
    context = cache.get(context_id, [])
    context.append(mr)

    # save context to cache
    cache.set(context_id, context, timeout=None)

def get_context(context_id, limit=10):
    prompt = ''
    context = cache.get(context_id, [])
    if context:
        history = context[-limit:]
        for convo in history:
            prompt += f"Customer said this: {convo['User']}\nAnd you responded with this: {convo['Response']} ---{convo['timestamp']}\n\n"
    
    return prompt
