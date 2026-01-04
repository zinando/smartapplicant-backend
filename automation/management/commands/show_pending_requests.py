from django.core.management.base import BaseCommand
from automation.helpers import get_pending_requests
from django.conf import settings

request_key = f"{settings.SMARTAPPLICANT.get('WABA_PHONE_NUMBER_ID')}_{str(2347031104270)}_pending_requests"

class Command(BaseCommand):
    help = "Show pending requests"

    def handle(self, *args, **kwargs):
        pending_requests = get_pending_requests(request_key)
        if not pending_requests:
            self.stdout.write("No pending requests found.")
            return

        for request in pending_requests:
            self.stdout.write(f"""
                Pending Request: {request}

                <<<----------------------------END----------------------------------->>>\n\n
            """)