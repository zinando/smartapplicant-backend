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
* params : biz_info (dict), page_id (str) 

- command : confirm_payment
* description : confirms the status of any transaction with a payment reference
* params : payment_ref

- command : get_secret_questions_for_client
* description : retrieves the secret questions set by the client and put them in context for AI use only. User must not be shown. Run this command before you update anything on the customer's record, then follow it with a message to the customer asking them if they are ready to answer their secret question. Their response will put the questions and answers in context.
* params : page_id (str)3

- command : update_secret_questions_for_client
* description : update the secret questions for a client after successful authentication. Ask the customer to provide answers to at least two of the questions correctly before you run this command. Also find if they want to update some or all the secret questions.
* params : page_id (str), secret_questions (str - E.g Q1: What is your mother's maiden name? A1: xxxx. Q2: What is your best friend's name in secondary school? A2: xxxx.)

- command : check_subscription_expiry
* description : checks if the subscription for a client is expired and updates the status accordingly
* params : page_id (str)
""".strip()

admin_legend = """
- command : close_pending_requests
* description : use this command to close pending requests that have been fully addressed by the business admin
* params : request_ids (list of str)
""".strip()