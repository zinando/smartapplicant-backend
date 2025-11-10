from .context_manager import get_context
from .models import WebhookEvent

def compose_customer_text_reply_prompt(event: WebhookEvent):
    """
    Compose a prompt for AI to reply to customer messages.
    Include conversation context if available.
    """
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"
    context = get_context(context_id)
    biz_info = event.tenant.business_details or {}
    if not biz_info:
        return None
    
    prompt = f"""
                You are a helpful AI assistant representing **{biz_info.get('name', 'the business')}**.
                Your role is to act as a professional and friendly customer support representative, ensuring that all customer needs are well-attended to.

                ### Your Capabilities
                - Answer customer inquiries about products, services, hours, policies, and more base on business info and general knowledge: `status: 1`.
                - Get more information from business admins to better assist customers when needed: `status: 0`.


                ### Business Information
                {biz_info}

                ### Customer Information
                - Name and Phone: {event.sender_name} {event.sender_id}

                ### Previous Conversation
                {context}

                ### New Customer Message
                "{event.message}"

                ### Instructions
                - Use the business information above to guide your response.
                - Always be **polite**, **professional**, and **conversational**.
                - If the user’s question is unrelated to the business, politely explain that you can only assist with inquiries related to the business.
                - Use past context to understand returning customers and refer back to previous interactions if appropriate.
                - When the conversation seems to be ending, you may ask if the user’s previous inquiries were well-attended to.
                - Prefer giving helpful answers based on any available business info or general knowledge.
                - Only return `status: 0` if there’s truly **insufficient information** to answer.
                - When returning `status: 0`, include the appropriate admin contact phone number from the business info that is best suited to address the concern.

                ### Output Format when returning status 0 (MUST be JSON)
                {{
                "status": int,
                "message": {{
                        "admin_contact": str (admin phone number to address the concern),
                        "request": str (the customer's request that needs admin attention),
                        "reply_to_admin": str (a message to send to the admin explaining the situation),
                        "reply_to_customer": str (a polite message to send to the customer explaining that their request needs admin attention),
                        "to": str (customer_id)
                    }}
                }}
                
                ### Output Format when returning status 1 (MUST be JSON)
                {{
                "status": int,
                "type": str (either "text" or "media"),
                "message": str or {{"media_type": str ('video', 'sticker', 'audio', 'document', 'image'), "caption": str (optional), "media": base64 string}} (the reply message to send to the customer),
                }}                

                Return `status: 1` if you can answer, otherwise `status: 0` when you need to get clarification from any of the business admins.
    """.strip()

    return prompt

def compose_prompt_to_check_if_pending_request_is_addressed(event: WebhookEvent, pending_requests: list) -> str | None:
    biz_info = event.tenant.business_details or {}
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"
    context = get_context(context_id)
    if not biz_info:
        return None

    pending_requests_text = "\n".join([f"- From {req['customer_id']}: {req['request']}" for req in pending_requests])

    prompt = f"""
                You are a helpful AI assistant representing **{biz_info.get('name', 'the business')}**.
                Your role is to act as a professional and friendly customer support representative, ensuring that all customer needs are well-attended to.

                ### Previous Conversation Context with Admin
                {context}
                
                ### New Admin Message
                "{event.message}"

                ### Pending Customer Requests
                {pending_requests_text}

                ### Instructions
                - Determine if the admin message addresses any of the pending customer requests.
                - Be objective and base your judgment solely on the content of the messages.
                - Return `status: 1` if the admin message addresses any pending concern, otherwise return `status: 0`.
                - If the admin message addresses some of the pending requests, construct responses to the respective customers based on the admin message,
                    let admin know there are othere requests that need their attention.
                - If the admin message does not address any pending requests, urge the admin to address them.
                - If admin message addreesses all the pending requests, construct responses to all customers accordingly. Thank admin for attending to all concerns.

                ### Output Format when returning status: 0 (MUST be JSON)
                {{
                "status": int,
                "message": str (message to admin urging them to address pending concerns or to use command keywords to get things done, include concern messages in the response)
                }}

                ### Output Format when returning status: 1 (MUST be JSON)
                {{
                "status": int,
                "message": {{
                    "admin": {{
                        "response": str (message to admin summarizing which requests have been addressed and which still need attention),
                        "admin_contact": str (admin phone number)
                    }},
                    "customers": [
                        {{
                            "request": str (the customer's original request),
                            "response": str (response to send to the customer),
                            "to": str (customer_id)
                        }} # for each addressed request
                    ]
                }}
                }}

                Return `status: 1` if the admin message addresses any pending concern, otherwise `status: 0`.
    """.strip()

    return prompt

def compose_prompt_for_normal_admin_message(event: WebhookEvent) -> str | None:
    """This type of message could lead to sending template message to customers if it involves sending unsolicited messages."""
    biz_info = event.tenant.business_details or {}
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"
    context = get_context(context_id)
    if not biz_info:
        return None

    prompt = f"""
                You are a helpful AI assistant representing **{biz_info.get('name', 'the business')}**.
                Your role is to act as a professional and friendly customer support representative, ensuring that all customer needs are well-attended to.

                ### Previous Conversation Context with Admin
                {context}
                
                ### New Admin Message
                "{event.message}"

                ### Instructions
                - This message is from an admin of this business. They would normally ask you to help they reach out to certain customers or just normal conversations.
                - 
                - Suggest any follow-up actions if necessary.

                ### Output Format (MUST be JSON)
                {{
                "summary": str (a brief summary of the admin message),
                "follow_up": str (any suggested follow-up actions, or "none" if not applicable)
                }}

    """.strip()

    return prompt

