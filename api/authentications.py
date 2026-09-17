from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import ServiceAPIKey


class ServiceAPIKeyAuthentication(BaseAuthentication):

    def authenticate(self, request):
        provided_key = request.headers.get("X-API-Key")

        if not provided_key:
            return None

        key_hash = ServiceAPIKey.hash_key(provided_key)

        try:
            key_obj = ServiceAPIKey.objects.get(
                key_hash=key_hash,
                is_active=True
            )
        except ServiceAPIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key.")

        key_obj.last_used_at = timezone.now()
        key_obj.save(update_fields=["last_used_at"])

        return (key_obj, key_obj)