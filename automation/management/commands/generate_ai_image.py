from django.core.management.base import BaseCommand
from api.ai import get_image_from_grok
# from automation.mydata import video_plan
# from automation.tasks import create_video_content, post_video_content_to_facebook
# from automation.models import AutomatedClients

prompt = """
            Ultra-realistic close-up beauty portrait of a female model with flawless skin and glossy lips, 
            studio lighting, soft glam makeup. She is gently placing her fingers near her lips to showcase an elegant, 
            long stiletto manicure. The nails feature a luxurious, trendy design (chrome finish, soft pink shimmer, 
            subtle glitter accents, high-gloss top coat). Sharp focus on nails, shallow depth of field, 
            premium beauty photography, high resolution, Instagram-ready, professional nail campaign style.
        """
class Command(BaseCommand):
    help = 'Generate an AI image with the given prompt'

    # def add_arguments(self, parser):
    #     parser.add_argument('page_id', type=str, help='Page ID for which to create the video')

    def handle(self, *args, **options):
        # page_id = options['page_id']
        image_data = get_image_from_grok(prompt)
        if image_data:
            self.stdout.write(self.style.SUCCESS(f'AI image generated successfully. Image data: {image_data}'))
            self.stdout.write(self.style.SUCCESS(f'Image URL: {image_data["image"]}'))
        else:
            self.stdout.write(self.style.ERROR('Failed to generate AI image'))  
        