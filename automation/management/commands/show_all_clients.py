from automation.models import AutomatedClients
from django.core.management.base import BaseCommand


clients = AutomatedClients.objects.all()
if not clients:
    raise Exception(f'No clients found.')
class Command(BaseCommand):
    help = "Trigger daily Facebook scheduling job"

    def handle(self, *args, **kwargs):
        for client in clients:
            assets_text = "***\n".join(client.business_assets) if client.business_assets else None
            self.stdout.write(f"""
                tenant: {client.tenant}
                auth_log: {client.auth_log}
                platform: {client.platform}
                client_id: {client.client_id}
                subscription_ref: {client.subscription_ref}
                subscription_expires_at: {client.subscription_expires_at.strftime("%d-%m-%Y") if client.subscription_expires_at else None}
                content_schedule_times: {client.content_schedule_times}
                page_access_token: {client.page_access_token}
                token_expires_at: {client.token_expires_at.strftime("%d-%m-%Y") if client.token_expires_at else None}
                subscribed: {client.subscribed}
                subscription_type: {client.subscription_type}
                created_at: {client.created_at.strftime("%d-%m-%Y") if client.created_at else None}
                business_details: \n{client.business_details}
                media_history: \n{client.media_history}
                evergreen_content: \n{client.evergreen_content}
                custom_prompts: \n{client.custom_prompts}
                saved_content: \n{client.saved_content}
                secret_questions: \n{client.secret_questions}
                Business Assets: \n\n{assets_text}
                <<<----------------------------END----------------------------------->>>\n\n
            """)