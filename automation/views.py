import json
import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .tasks import handle_inbound_event
from .content_automation.facebook import AutomateFacebookPost
from .helpers import save_cache, get_cache
from api.email_service import send_email

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
                    msg = payload["entry"][0]["changes"][0]["value"]["messages"][0]
                    message_id = msg["id"]
                    logger.info(f'message ID: {message_id}')
                    if get_cache(message_id):
                        return JsonResponse({"status": "received"}) # already processed
                    save_cache(message_id,True,15)
                    
                    handle_inbound_event.delay(payload)  # celery
                    # logger.info('received new instruction to post')
                    # auto = AutomateFacebookPost("750798604776594")
                    # send_email("This is a test email from webhook_entry", "belovedsamex@yahoo.com")
                    # auto.make_a_test_post()
    
    return JsonResponse({"status": "received"})
