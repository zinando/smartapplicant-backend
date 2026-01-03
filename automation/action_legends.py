legend = """
- command : send_message_to_admin
* description : send message to an appropriate admin contact
* params : message, contact

- command : send_message_to_customer
* description : send message to a customer as maybe requested by an admin
* params : message, contact

- command : register_new_facebook_page_for_content_automation
* description : register a new facebook page for content automation
* params : page_id (str), platform (str - facebook or instagram), session_id (str), secret_questions (str - Q1: What is your mother's maiden name? A1: xxxx. Q2: What is your best friend's name in secondary school? A2: xxxx. Q3: What is the last primary school you attended? A3: xxxx.)

- command : subscribe_to_post_automation
* description : subscribe for an automated client for facebook page post automation
* params : subscription_days (int - 30 for regular, 3 for trial period), page_id (str), payment_ref (str - not required for trial period subscription) 

- command : update_client_info
* description : update the business details of automated clients for facebook page post automation
* params : biz_nfo (dict), page_id (str) 

- command : confirm_payment
* description : confirms the status of any transaction with a payment reference
* params : payment_ref

- command : get_secret_questions_for_client
* description : retrieves the secret questions set by the client and put them in context for AI use only. User must not be shown. Run this command before you update anything on the customer's record, then follow it with a message to the customer asking them if they are ready to answer their secret question. Their response will put the questions and answers in context.
* params : page_id (str)

""".strip()