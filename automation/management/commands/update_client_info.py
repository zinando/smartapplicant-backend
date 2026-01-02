from automation.ai_commands import update_info_for_client
from automation.models import AutomatedClients

biz_info = {}
page_id = ''
custom_prompt = {}


message = update_info_for_client(
    biz_info=biz_info,
    page_id=page_id
)

print(f'Message: \n{message}') 