# permissions.py
from django.utils import timezone
from rest_framework.permissions import BasePermission

class HasServiceAPIKey(BasePermission):
    def has_permission(self, request, view):
        from api.models import ServiceAPIKey

        provided_key = request.headers.get('X-API-Key')
        if not provided_key:
            return False

        key_hash = ServiceAPIKey.hash_key(provided_key)

        try:
            key_obj = ServiceAPIKey.objects.get(key_hash=key_hash, is_active=True)
        except ServiceAPIKey.DoesNotExist:
            return False

        key_obj.last_used_at = timezone.now()
        key_obj.save(update_fields=['last_used_at'])
        return True