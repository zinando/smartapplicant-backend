from automation.models import AutomatedClients

page_id = ''
if not page_id:
    raise Exception('No page id provided')
client = AutomatedClients.objects.filter(client_id=page_id).first()
if not client:
    raise Exception(f'Client with ID {page_id} not found.')
print(f"""
    tenant: {client.tenant}
    auth_log: {client.auth_log}
    platform: {client.platform}
    client_id: {client.client_id}
    subscription_ref: {client.subscription_ref}
    subscription_expires_at: {client.subscription_expires_at.strftime("%d-%m-%Y") if client.subscription_expires_at else None}
    content_schedule_times: {client.content_schedule_times}
    page_access_token: {client.page_access_token}
    token_expires_at: {client.token_expires_at.strftime("%d-%m-%Y") if client.token_expires_at else None}
    subscribed: {client.subscribed}
    subscription_type: {client.subscription_type}
    created_at: {client.created_at.strftime("%d-%m-%Y") if client.created_at else None}
    business_details: \n{client.business_details}
    media_history: \n{client.media_history}
    evergreen_content: \n{client.evergreen_content}
    custom_prompts: \n{client.custom_prompts}
    saved_content: \n{client.saved_content}
    secret_questions: \n{client.secret_questions}
""")