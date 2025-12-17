legend = """
- command : send_message_to_admin
* description : send message to an appropriate admin contact
* params : message, contact

- command : send_message_to_customer
* description : send message to a customer as maybe requested by an admin
* params : message, contact

- command : register_new_facebook_page_for_content_automation
* description : register a new facebook page for content automation
* params : page_id, session_id, platform, payment_ref

- command : confirm_payment
* description : confirms the status of any transaction with a payment reference
* params : payment_ref

""".strip()