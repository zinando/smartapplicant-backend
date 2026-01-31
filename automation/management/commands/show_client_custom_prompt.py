from automation.models import AutomatedClients
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Show custom prompt used to generate facebook content for client with ID"

    def add_arguments(self, parser):
        parser.add_argument('page_id', type=str, help='ID of the page whose custom prompt is to be shown.')

    def handle(self, *args, **kwargs):
        page_id = kwargs['page_id']
        client = AutomatedClients.objects.filter(client_id=page_id).first()
        if client:
            self.stdout.write(f"""
                ******CUSTOM PROMPT**********\n\n
                {client.custom_prompts}
            """)
        else:
            self.stdout.write(f"Client with ID {page_id} not found.")