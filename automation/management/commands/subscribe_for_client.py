from automation.ai_commands import subscribe
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Subscribe a client for a given number of days'

    def add_arguments(self, parser):
        parser.add_argument('subscription_days', type=int, help='Number of days to subscribe the client for')
        parser.add_argument('page_id', type=str, help='Page ID of the client to subscribe')
        parser.add_argument('amount', type=float, help='Amount paid for the subscription')

    def handle(self, *args, **options):
        subscription_days = options['subscription_days']
        page_id = options['page_id']
        amount = options['amount']
        message = subscribe(
            subscription_days=subscription_days,
            page_id=page_id,
            amount=amount,
            method='manual'
        )

        self.stdout.write(self.style.SUCCESS(f'Message: \n{message}'))