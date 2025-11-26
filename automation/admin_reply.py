from .models import WebhookEvent
from .helpers import get_pending_requests
from .prompts import compose_prompt_to_check_if_pending_request_is_addressed, compose_prompt_for_normal_admin_message

def process_admin_message(event: WebhookEvent):
    """
    Process admin messages that are not commands.
    Example scenarios:
    - Admin responding to customer inquiries
    - Admin providing additional information
    Rule:
    - Admin must attend to all pending requests in their queue before sending new messages.
    """
    # first, check if admin has pending requests
    request_key = f"{event.tenant.waba_phone_number_id}_{event.sender_id}_pending_requests"
    pending_requests = get_pending_requests(request_key)

    if not pending_requests:
        print("no pending requests")
        # No pending requests, process normal admin message
        return compose_prompt_for_normal_admin_message(event)

    # there are pending requests, check if admin is responding to any
    # requests = [{
    #     ""
    #     "customer_id": req["customer_id"],
    #     "request": req["request"]
    # } for req in pending_requests
    # ]
    print("there are pending requests")
    return compose_prompt_to_check_if_pending_request_is_addressed(event, pending_requests)
