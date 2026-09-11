# automation/management/commands/post_fb_test.py

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Post a test message to a Facebook Page using its stored Page Access Token."

    def add_arguments(self, parser):
        parser.add_argument(
            "page_id",
            type=str,
            help="The Facebook Page ID to post to.",
        )

    def handle(self, *args, **options):
        page_id = options["page_id"]

        page_access_token = self._get_page_token(page_id)
        self._post_test_content(page_id, page_access_token)

    def _get_page_token(self, page_id):
        from automation.models import AutomatedClients  # adjust import path as needed

        try:
            client = AutomatedClients.objects.get(client_id=page_id)
        except AutomatedClients.DoesNotExist:
            raise CommandError(f"No AutomatedClients record found for page_id={page_id!r}")

        if not client.page_access_token:
            raise CommandError(f"page_access_token is empty for page_id={page_id!r}")

        return client.page_access_token

    def _post_test_content(self, page_id, page_access_token):
        url = f"{settings.META_GRAPH_URL}/{page_id}/feed"
        msgs = {
            # smartapplicant page
            '750798604776594': "SmartApplicant is a platform that helps businesses automate their social media presence and engage with their audience effectively.",
            # Smart & Trendy Blitz, a thrift clothing store
            '823731924160674': "Smart & Trendy Blitz is a thrift clothing store that offers a curated selection of stylish and affordable second-hand fashion.",
            # Lazy.News.Men
            '423001724240260': "Lazy.News.Men is a news outlet that covers the latest happenings in the world of lazy living."
        }

        payload = {
            "message": msgs.get(page_id, "This is a test post from SmartApplicant."),
            "access_token": page_access_token,
        }

        try:
            response = requests.post(url, data=payload, timeout=15)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as e:
            # Facebook errors often arrive as a JSON body even on non-200 status,
            # so try to surface that instead of just the raw exception.
            try:
                error_body = response.json()
                raise CommandError(f"Facebook API error: {error_body.get('error', error_body)}")
            except (NameError, ValueError):
                raise CommandError(f"Request to Facebook failed: {e}")
        except ValueError:
            raise CommandError("Facebook returned invalid JSON.")

        if "error" in result:
            self.stdout.write(self.style.ERROR(f"Facebook API error: {result['error']}"))
            return

        post_id = result.get("id")
        self.stdout.write(self.style.SUCCESS(f"✅ Test post created successfully. Post ID: {post_id}"))