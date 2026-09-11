# automation/management/commands/check_fb_token.py

import json
import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Check the validity of a Facebook access token via the Graph API debug_token endpoint."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--token",
            type=str,
            help="A raw Facebook access token to check directly.",
        )
        group.add_argument(
            "--state",
            type=str,
            help="A FacebookAuthLog.state value — the command will look up its stored long-lived token.",
        )

    def handle(self, *args, **options):
        token = options.get("token")
        state = options.get("state")

        if state:
            token = self._get_token_from_state(state)

        if not token:
            raise CommandError("No token resolved to check.")

        self._debug_token(token)

    def _get_token_from_state(self, state):
        from automation.models import FacebookAuthLog  # adjust import path as needed

        auth_log = FacebookAuthLog.objects.filter(state=state).first()
        if not auth_log:
            raise CommandError(f"No FacebookAuthLog found for state={state!r}")

        payload = auth_log.long_lived_token_payload
        if not payload:
            raise CommandError(f"long_lived_token_payload is empty for state={state!r}")

        try:
            data = json.loads(payload)
        except (TypeError, json.JSONDecodeError) as e:
            raise CommandError(f"Could not parse long_lived_token_payload: {e}")

        token = data.get("access_token")
        if not token:
            raise CommandError("No access_token found in long_lived_token_payload.")

        return token

    def _debug_token(self, token):
        app_id = settings.SMARTAPPLICANT["APP_ID"]
        app_secret = settings.SMARTAPPLICANT["APP_SECRET"]
        app_access_token = f"{app_id}|{app_secret}"

        url = (
            f"{settings.META_GRAPH_URL}/debug_token"
            f"?input_token={token}"
            f"&access_token={app_access_token}"
        )

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as e:
            raise CommandError(f"Request to Facebook failed: {e}")
        except ValueError:
            raise CommandError("Facebook returned invalid JSON.")

        if "error" in result:
            self.stdout.write(self.style.ERROR(f"Facebook API error: {result['error']}"))
            return

        data = result.get("data", {})

        is_valid = data.get("is_valid")
        expires_at = data.get("expires_at")
        scopes = data.get("scopes", [])
        error_info = data.get("error")

        self.stdout.write(self.style.MIGRATE_HEADING("Token Debug Result"))
        self.stdout.write(f"  Valid:      {is_valid}")
        self.stdout.write(f"  App ID:     {data.get('app_id')}")
        self.stdout.write(f"  User ID:    {data.get('user_id')}")
        self.stdout.write(f"  Type:       {data.get('type')}")
        self.stdout.write(f"  Expires at: {expires_at} (0 = never expires)")
        self.stdout.write(f"  Scopes:     {', '.join(scopes) if scopes else 'none'}")

        if error_info:
            self.stdout.write(self.style.ERROR(f"  Error:      {error_info}"))

        if is_valid:
            self.stdout.write(self.style.SUCCESS("\n✅ Token is currently valid."))
        else:
            self.stdout.write(self.style.ERROR("\n❌ Token is invalid or expired."))