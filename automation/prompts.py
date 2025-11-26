from .context_manager import get_context
from .models import WebhookEvent
from .action_legends import legend

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
                - When you need to get more info from an admin concerning a customer's enquiry, use the 'actions' to create a message to be routed to the appropriate admin for this business, the admin will reply you and if the response is sufficient you use the admin reply to address the customer's question.
                - You can command as many actions as possible based on available actions in the actions legend below.
                
                ### Output Format (MUST be JSON)
                {{
                    "reply": {{
                        "to": "customer number",
                        "message": "Message to the customer."
                    }},
                    "actions": [
                        {{
                            "command": "send_message_to_admin",
                            "params": {{
                                "message":"Summary of your conversation with customer, and the question you want the admin to answer",
                                "contact":"Admin number from business info: e.g 234701104270",
                            }},
                            "expect_reply": True (to show if the action requires a response from recipient or not)
                        }}
                    ]
                }}

                * Leave the actions field empty if there is no need for extra actions to be taken. Use the Legend below to know the various actions you can command alongside your response to any message

                ### Actions Legend
                {legend}
                """.strip()

    return prompt

def compose_prompt_to_check_if_pending_request_is_addressed(event: WebhookEvent, pending_requests: list) -> str | None:
    biz_info = event.tenant.business_details or {}
    context_id = f"{event.tenant.waba_phone_number_id}_{event.sender_id}"
    context = get_context(context_id)
    if not biz_info:
        return None

    pending_requests_text = "\n".join([f"Event ID: {req['event_id']}\n- From {req['customer_id']}: {req['request']}" for req in pending_requests])

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
                - Return only `status: 0`.
                - If the admin message addresses some of the pending requests, construct responses to the respective customers based on the admin message,
                    let admin know there are othere requests that need their attention.
                - If the admin message does not address any pending requests, urge the admin to address them and return empty list for customers.
                - If admin message addreesses all the pending requests, construct responses to all customers accordingly. Return empty dict for admin.

                ### Output Format when returning status: 1 (MUST be JSON)
                {{
                "status": 0,
                "type": "text or media (message format)",
                "message": {{
                    "admin": {{
                        "response": str (message to admin summarizing which requests have been addressed and which still need attention),
                        "admin_contact": str (admin phone number)
                    }},
                    "customers": [
                        {{
                            "event_id": str (event id from the pending customer request),
                            "request": str (the customer's original request unaltered),
                            "response": str (response to send to the customer),
                            "to": str (customer_id)
                        }} # for each addressed request
                    ]
                }}
                }}

                Return only `status: 0`.
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
                This message is from an admin of the business, and you are to respond like a loyal subbordinate AI assistant. Use Sir/Ma'am/Boss whenever possible.

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
                "message": str (a brief summary of the admin message),
                "follow_up": str (any suggested follow-up actions, or "none" if not applicable)
                }}

    """.strip()

    return prompt

