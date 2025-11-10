"""This module provides functionality for executing automated tasks by executing the script"""

from .actions import add_tenant, add_client
from .mydata import tenant
from django.utils import timezone


# # Example usage: add a new tenant
# new_tenant = add_tenant(
#     name=tenant["name"],
#     waba_id=tenant["waba_id"],
#     waba_phone_number=tenant["waba_phone_number"],
#     waba_phone_number_id=tenant["waba_phone_number_id"],
#     business_details=tenant.get("business_details", {}),
#     fb_page_id=tenant.get("fb_page_id"),
#     ig_business_account_id=tenant.get("ig_business_account_id"),
#     tg_bot_username=tenant.get("tg_bot_username"),
#     custom_prompts=tenant.get("custom_prompts", {}),
#     content_schedule_times=tenant.get("content_schedule_times", {}),
#     media_history=tenant.get("media_history", []),
#     evergreen_content=tenant.get("evergreen_content", []),
#     customers=tenant.get("customers", []),
# )
# print(f"Added new tenant: {new_tenant}")
# # add a new automated client for the tenant
# new_client = add_client(
#     tenant=new_tenant,
#     platform="facebook",
#     client_id="750798604776594",
#     access_token="secure_access_token",
#     token_expires_at=None,
#     subscribed=True,
#     subscription_ref="sub_ref_001",
#     subscription_expires_at=timezone.now() + timezone.timedelta(days=30)
# )