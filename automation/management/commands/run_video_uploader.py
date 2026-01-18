from django.core.management.base import BaseCommand
from automation.mydata import video_plan
from automation.tasks import create_video_content, post_video_content_to_facebook
from automation.models import AutomatedClients

class Command(BaseCommand):
    help = 'Create a video for a given page ID based on its video plan'

    def add_arguments(self, parser):
        parser.add_argument('page_id', type=str, help='Page ID for which to create the video')

    def handle(self, *args, **options):
        page_id = options['page_id']
        path = "temp_media/Smartapplicant.mp4"
        client = AutomatedClients.objects.filter(client_id=page_id).first()
        video_plan["final_video_path"] = path
        # self.stdout.write(self.style.HTTP_INFO(f'Business info: {client.business_details}'))
        video_plan["caption"] = "Are you planning on creating a job-winning Resume/CV soon?"
        client.saved_video_plan = video_plan
        client.save(update_fields=["saved_video_plan"])

        # create_video_content.delay(page_id, video_plan)
        post_video_content_to_facebook.delay(page_id)
        self.stdout.write(self.style.SUCCESS(f'Video content task dispatched for page: {page_id}'))