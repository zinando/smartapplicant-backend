from automation.video_generator import VideoGenerator
from django.core.management.base import BaseCommand
from api.ai import try_call_tts
from automation.mydata import video_plan

class Command(BaseCommand):
    help = 'Create a video for a given page ID based on its video plan'

    # def add_arguments(self, parser):
    #     parser.add_argument('page_id', type=str, help='Page ID for which to create the video')

    def handle(self, *args, **options):
        # page_id = options['page_id']
        # audio_path, status = try_call_tts("This is a test voice over for the video.")
        # self.stdout.write(self.style.SUCCESS(f'Generated audio at: {audio_path}'))
        generator = VideoGenerator(video_plan=video_plan)
        video_path, message = generator.render()
        # watermark = generator.make_watermark("SmartApplicant", duration=15)
        # self.stdout.write(self.style.SUCCESS(f'Created watermark clip: {watermark}'))

        self.stdout.write(self.style.SUCCESS(f'Video created at: {video_path}'))