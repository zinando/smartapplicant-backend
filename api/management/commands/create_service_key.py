import secrets 
from django.core.management.base import BaseCommand 

class Command(BaseCommand): 
    help = 'Generate a new service API key' 
    
    def add_arguments(self, parser):
         parser.add_argument('name', type=str) 
    
    def handle(self, *args, **options): 
        from api.models import ServiceAPIKey 
        
        raw_key = secrets.token_urlsafe(48)
        ServiceAPIKey.objects.create(
            name=options['name'],
            key_hash=ServiceAPIKey.hash_key(raw_key)
        )

        self.stdout.write(self.style.SUCCESS(f'Created key for "{options["name"]}":')) 
        self.stdout.write(raw_key) 
        self.stdout.write('Save this now — store it in n8n credentials immediately.')
