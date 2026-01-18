from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from typing import List, Optional
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, subject: str, to_emails: list, context: dict, template_name: str, from_email: Optional[str] = None):
        self.subject = subject
        self.to_emails = to_emails
        self.context = context
        self.template_name = template_name
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL
        self.email_host = settings.EMAIL_HOST
        self.email_port = settings.EMAIL_PORT
        self.email_user = settings.EMAIL_HOST_USER
        self.email_password = settings.EMAIL_HOST_PASSWORD

    def send_email(self) -> bool:
        try:
            # Render templates
            html_content = render_to_string(self.template_name, self.context)
            text_content = render_to_string(self.template_name.replace(".html", ".txt"), self.context)

            for recipient in self.to_emails:
                msg = MIMEMultipart()
                msg["From"] = self.from_email
                msg["To"] = recipient
                msg["Subject"] = self.subject

                # Add both plain text and HTML versions
                msg.attach(MIMEText(text_content, "plain"))
                msg.attach(MIMEText(html_content, "html"))

                # Send using SMTP
                with smtplib.SMTP(self.email_host, self.email_port) as server:
                    server.starttls()
                    server.login(self.email_user, self.email_password)
                    server.send_message(msg)

            logger.info(f"[EmailService] Email sent to {self.to_emails}")
            return True

        except Exception as e:
            logger.exception("[EmailService] Failed to send email")
            return False
class DjangoEmailService:
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
            response = msg.send()
            logger.info(f"[EmailService] Email sent to {self.to_emails} with response: {response}")
            return True
        except Exception as e:
            # Optional: Log the error
            logger.error(f"[EmailService] Failed to send email: {e}")
            return False


def send_email(body, recipient):
    """Send an email notification."""
    msg = MIMEMultipart()
    msg["From"] = 'Smart Applicant <contact@smartapplicant.net>'
    msg["To"] = recipient
    msg["Subject"] = 'Facebook Post Automation Report'
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP('workplace.truehost.cloud', 587) as server:
            server.starttls()
            server.login('contact@smartapplicant.net', 'YOUAREmad2#')
            server.send_message(msg)
            logger.info("📧 Email notification sent.")
    except Exception as e:
        logger.error(f"⚠️ Failed to send email: {e}")
