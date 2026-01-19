from automation.video_generator import VideoGenerator
from automation.tasks import create_video_content, post_video_content_to_facebook
from automation.models import AutomatedClients
from django.core.management.base import BaseCommand
from api.ai import try_call_tts
from automation.mydata import video_plan, assets

class Command(BaseCommand):
    help = 'Create a video for a given page ID based on its video plan'

    def add_arguments(self, parser):
        parser.add_argument('page_id', type=str, help='Page ID for which to create the video')

    def handle(self, *args, **options):
        page_id = options['page_id']
        create_video_content.delay(page_id)
        # post_video_content_to_facebook.delay(page_id)
        self.stdout.write(self.style.SUCCESS(f'Video creation task dispatched.'))