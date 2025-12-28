from django.core.management.base import BaseCommand
from automation.tasks import schedule_facebook_post

class Command(BaseCommand):
    help = "Trigger daily Facebook scheduling job"

    def handle(self, *args, **kwargs):
        schedule_facebook_post.delay()
        self.stdout.write("Facebook scheduling task dispatched")
