import pytest
from automation.content_automation.facebook import AutomateFacebookPost
import logging
from api.ai import get_structured_data_from_gemini

logger = logging.getLogger(__name__)


def test_facebook_post_instance_creation(db, app_client, app_tenant):
    fb = AutomateFacebookPost(page_id="750798604776594")

    assert fb.page_id == "750798604776594"
    # logger.info(f"Bussiness details: {fb.get_business_details()}")3
    assert isinstance(fb.get_business_details(), dict)

def test_content_prompt_generation(db, app_client, app_tenant):
    fb = AutomateFacebookPost(page_id=app_client.client_id)

    prompt = fb.get_content_prompt()
    schedule_times = fb.get_schedule_times()
    contents = get_structured_data_from_gemini(prompt)
    logger.info(f"Generated Contents: {contents}")
    # logger.info(f"Schedule Times: {schedule_times}")
    # logger.info(f"Client schedule times: {app_client.content_schedule_times}")
    # logger.info(f"Generated Prompt: {prompt}")
    
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert isinstance(schedule_times, list)
    assert len(schedule_times) > 0
    assert isinstance(contents, list)
    assert len(contents) > 0

# def test_ai_generated_content(db, app_client, app_tenant):
#     fb = AutomateFacebookPost(page_id=app_client.client_id)

#     prompt = fb.get_content_prompt()
#     ai_content = fb.generate_ai_content(prompt)

#     # logger.info(f"AI Generated Content: {ai_content}")
#     assert isinstance(ai_content, str)
#     assert len(ai_content) > 0
