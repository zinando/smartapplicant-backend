from automation.ai_commands import subscribe

subscription_days = 3
page_id = ''
payment_ref = ''

message = subscribe(
    subscription_days=subscription_days,
    page_id=page_id,
    payment_ref=payment_ref
)

print(f'Message: \n{message}')