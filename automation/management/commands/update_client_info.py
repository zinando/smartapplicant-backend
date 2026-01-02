from automation.ai_commands import update_info_for_client
from automation.models import AutomatedClients
from django.core.management.base import BaseCommand
from automation.mydata import custom_prompts

biz_info = {}
page_id = '750798604776594'
media_history = [] # [{"id": "media_id", "caption": "caption text"}]
evergreen_content = []  # list of evergreen text content items, can be used on any platform ["text content 1", "text content 2"]
content_schedule_times = []  # preferred times to post content [7, 9, 12, 15, 18, 21]
page_access_token = 'EAA5jssqcb0kBPwKYDLGcAbrEBZBNmMqc1cv4TmJ5Y2WAYQZB4ZCoP3XsZBN3dOBdB8t9wAmEWiYVGDbSFFmX73QN9Ch2ZAttFdpxIOm21kcA7X9bVdHEvJN5s62fbACRcRrq9pU8CZCkW21ZBuK6fB9HZC8QokYZBs9utzIiNZBnkbXPxPyZB4tiBcjtIAYJ3HM9s05ZAAlwbpQpRTbwy17niqmJ4AZDZD'
saved_content = []  # content saved for posting later [{"content": "text or media", "content_type": "text/image/link", "caption": "caption text", "comments": []}]
secret_questions = "Q: Mother's maiden name? A: Isietu. Q: Best friend's name in Logiss (my secondary school)? A: Ikechukwu Nnadilim. Q: last primary school attended? A: Pioneer Primary School, Edenta, Awo-Idemili, Imo State."  # secret questions set by account owner for authentication purpose before any modification on account information [{'question':'answer'}...]
subscription_type = "txt-img"

message = ''
if biz_info:
    message = update_info_for_client(
        biz_info=biz_info,
        page_id=page_id
    )
client = AutomatedClients.objects.filter(client_id=page_id).first()
if not client:
    raise Exception(f"Client with ID {page_id} not found.")

class Command(BaseCommand):
    help = "Updates selected automated client with the provided information"
    def handle(self, *args, **kwargs):
        client.custom_prompts = custom_prompts or client.custom_prompts
        client.media_history = media_history or client.media_history
        client.evergreen_content = evergreen_content or client.evergreen_content
        client.content_schedule_times = content_schedule_times or client.content_schedule_times
        client.page_access_token = page_access_token or client.page_access_token
        client.saved_content = saved_content or client.saved_content
        client.secret_questions = secret_questions or client.secret_questions
        client.subscription_type = subscription_type or client.subscription_type
        client.save()
        self.stdout.write('Client updated with new information')

        self.stdout.write(f'Message: \n{message}')