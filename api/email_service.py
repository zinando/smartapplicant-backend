from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from typing import List, Optional


class EmailService:
    def __init__(self, subject: str, to_emails: List[str], context: dict, template_name: str, from_email: Optional[str] = None):
        self.subject = subject
        self.to_emails = to_emails
        self.context = context
        self.template_name = template_name
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL

    def send_email(self) -> bool:
        try:
            html_content = render_to_string(self.template_name, self.context)
            text_content = render_to_string(self.template_name.replace('.html', '.txt'), self.context)

            msg = EmailMultiAlternatives(
                subject=self.subject,
                body=text_content,
                from_email=self.from_email,
                to=self.to_emails
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return True
        except Exception as e:
            # Optional: Log the error
            print(f"[EmailService] Failed to send email: {e}")
            return False
