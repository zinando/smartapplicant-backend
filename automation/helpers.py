from django.core.cache import cache
import re

def remove_business_info_blocks(text: str) -> str:
    """
    Removes all <---start: Business Information ----> ... <---end: Business Information ----> blocks from a string.
    """
    return re.sub(
        r"<-start: Business Information ->.*?<-end: Business Information ->", 
        "", 
        text, 
        flags=re.DOTALL
    ).strip()

def save_cache(key, value, timeout= 60*60*24):
    """Saves item in flask cahe"""
    cache.set(key, value, timeout=timeout)
    return f"Saved: {key} = {value}"

def get_cache(key):
    return cache.get(key) or None

def delete_cache(key):
    cache.delete(key)
    return f"Deleted: {key}"

def remove_cache_item(key, item):
    """Removes an item from a cached list"""
    cached_list = get_cache(key) or []
    if item in cached_list:
        cached_list.remove(item)
        save_cache(key, cached_list)
        return f"Removed {item} from {key}"
    return f"{item} not found in {key}"

def add_cache_item(key, item):
    """Adds an item to a cached list"""
    cached_list = get_cache(key) or []
    if item not in cached_list:
        cached_list.append(item)
        save_cache(key, cached_list)
        return f"Added {item} to {key}"
    return f"{item} already in {key}"

def clear_cache():
    cache.clear()
    return "Cache cleared"

def log_pending_request(key, value):
    """Logs a pending request in cache"""
    pending_requests = get_cache(key) or []
    pending_requests.append(value)
    save_cache(key, pending_requests)
    return f"Logged pending request under {key}"

def get_pending_requests(key):
    """Retrieves pending requests from cache"""
    return get_cache(key) or []

def remove_pending_request(key, event_id):
    """Removes pending request from cache"""
    items = get_pending_requests(key)
    if items:
        new_items = [my for my in items if my['event_id'] != event_id]
        save_cache(key, new_items)
        return f'pending request with event id {event_id} removed from list.'
    return ''