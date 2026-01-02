from automation.models import AutomatedClients
from automation.ai_commands import add_new_client

def add_client(tenant, platform, client_id, access_token, token_expires_at=None,
               subscribed=False, subscription_ref=None, subscription_expires_at=None):
    # client = AutomatedClients(
    #     tenant=tenant,
    #     platform=platform,
    #     client_id=client_id,
    #     access_token=access_token,
    #     token_expires_at=token_expires_at,
    #     subscribed=subscribed,
    #     subscription_ref=subscription_ref,
    #     subscription_expires_at=subscription_expires_at
    # )
    # client.save()
    client, created = AutomatedClients.objects.get_or_create(
        client_id=client_id,
        defaults={
            'tenant': tenant,
            'platform': platform,
            'page_access_token': access_token,
            'token_expires_at': token_expires_at,
            'subscribed': subscribed,
            'subscription_ref': subscription_ref,
            'subscription_expires_at': subscription_expires_at
        }
    )
    return client

def update_client_subscription(client: AutomatedClients, subscribed: bool, subscription_expires_at=None):
    client.subscribed = subscribed
    client.subscription_expires_at = subscription_expires_at 
    client.save(update_fields=['subscribed', 'subscription_expires_at'])


platform = 'facebook'
page_id = ''
session_id = ''
secret_questions = {}

message, form = add_new_client(
    page_id=page_id,
    platform=platform,
    session_id=session_id,
    secret_questions=secret_questions
)

print(f'returned message: \n{message}')
print(f'\nForm: \n{form}')

