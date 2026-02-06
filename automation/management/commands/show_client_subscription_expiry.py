from automation.ai_commands import get_subscription_expiry
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Show subscription expiry date for a client'

    def add_arguments(self, parser):
        parser.add_argument('page_id', type=str, help='Page ID of the client to subscribe')

    def handle(self, *args, **options):
        page_id = options['page_id']
        message = get_subscription_expiry(page_id=page_id)

        self.stdout.write(self.style.SUCCESS(f'Message: \n{message}'))