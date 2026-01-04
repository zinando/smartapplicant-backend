from django.core.management.base import BaseCommand
from automation.helpers import remove_pending_request, get_pending_requests
from django.conf import settings

request_key = f"{settings.SMARTAPPLICANT.get('PHONE_NUMBER_ID')}_{str(2347031104270)}_pending_requests"
request_ids = [96, 107, 110]

class Command(BaseCommand):
    help = "Remove a pending request"

    def handle(self, *args, **kwargs):
        for request_id in request_ids:
            result = remove_pending_request(request_key, request_id)
            self.stdout.write(result)