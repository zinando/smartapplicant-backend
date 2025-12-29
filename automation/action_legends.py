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

- command : subscribe_to_post_automation
* description : subscribe for an automated client for facebook page post automation
* params : subscription_days (int - 30 for regular, 3 for trial period), page_id (str), payment_ref (str - not required for trial period subscription) 

- command : update_client_info
* description : update the business details of automated clients for facebook page post automation
* params : biz_nfo (dict), page_id (str) 

- command : confirm_payment
* description : confirms the status of any transaction with a payment reference
* params : payment_ref

""".strip()