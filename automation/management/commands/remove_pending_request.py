from django.core.management.base import BaseCommand
from automation.helpers import remove_pending_request, get_pending_requests

request_key = ''
request_id = ''

class Command(BaseCommand):
    help = "Remove a pending request"

    def handle(self, *args, **kwargs):
        success = remove_pending_request(request_key, request_id)
        # check if removal was successful
        requests = get_pending_requests(request_key)
        for req in requests:
            if req.get('request_id') == request_id:
                self.stdout.write(f"Failed to remove pending request with ID: {request_id}")
                break
        else:
            self.stdout.write(f"Successfully removed pending request with ID: {request_id}")
            