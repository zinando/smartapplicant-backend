import json
import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .tasks import handle_inbound_event 

logger = logging.getLogger(__name__)

VERIFY_TOKEN = settings.WEBHOOK_VERIFY_TOKEN  # set in env

@require_http_methods(["GET", "POST"])
@csrf_exempt
def webhook_entry(request):
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponse("Verification failed", status=403)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        payload = {}
        return HttpResponse("Invalid payload", status=400)
    
    # handle only message payloads
    if "entry" in payload:
        if "changes" in payload["entry"][0]:
            if "value" in payload["entry"][0]["changes"][0]:
                if "messages" in payload["entry"][0]["changes"][0]["value"]:
                    from .execute import new_client
                    handle_inbound_event.delay(payload)  # celery
    
    return JsonResponse({"status": "received"})
