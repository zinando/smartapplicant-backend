from automation.models import FacebookAuthLog
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Display FacebookAutholog instance given the page_id"

    def handle(self, *args, **kwargs):
        page_id = ''
        autolog = FacebookAuthLog.objects.all()
        if autolog:
            for log in autolog:
                message = f"""
                        State (session_id): {log.state}
                        IP Address: {log.ip_address}
                        User Agent: {log.user_agent}
                        Step: {log.step}
                        Step status: {log.step_status}
                        Code: {log.code}
                        Message: {log.message}
                        Created at: {log.created_at.strftime('%d-%m-%Y') if log.created_at else None}
                        Short-lived Token Payload: \n{log.short_lived_token_payload}\n
                        Long-lived Token Payload: \n{log.long_lived_token_payload}\n
                        Page-access Token Payload: \n{log.page_access_token_payload}
                        <<<<<-------------------------End---------------------->>>>>>>>>>>>
                    """.strip()
        else:
            message = "No FacebookAutolog record found."
        self.stdout.write(message)