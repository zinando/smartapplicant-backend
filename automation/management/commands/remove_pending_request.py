from django.core.management.base import BaseCommand
from automation.helpers import remove_pending_request, get_pending_requests
from django.conf import settings

request_key = f"{settings.SMARTAPPLICANT.get('PHONE_NUMBER_ID')}_{str(2347031104270)}_pending_requests"
request_id = 92

class Command(BaseCommand):
    help = "Remove a pending request"

    def handle(self, *args, **kwargs):
        success = remove_pending_request(request_key, request_id)
        # check if removal was successful
        requests = get_pending_requests(request_key)
        for req in requests:
            if str(req.get('event_id')) == str(request_id):
                self.stdout.write(f"Failed to remove pending request with ID: {request_id}")
                break
        else:
            self.stdout.write(f"Successfully removed pending request with ID: {request_id}")
            