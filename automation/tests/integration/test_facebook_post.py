import pytest
from automation.content_automation.facebook import AutomateFacebookPost
import logging
from api.ai import get_structured_data_from_gemini
from automation.mydata import sample_content
from django.conf import settings
import requests
from automation.tasks import schedule_facebook_post

logger = logging.getLogger(__name__)


def test_facebook_post_instance_creation(db, app_client, app_tenant):
    fb = AutomateFacebookPost(page_id="750798604776594")

    assert fb.page_id == "750798604776594"
    # logger.info(f"Bussiness details: {fb.get_business_details()}")
    assert isinstance(fb.get_business_details(), dict)

def t_content_prompt_generation(db, app_client, app_tenant):
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

def t_link_posting(db, app_client, app_tenant):
    fb = AutomateFacebookPost(page_id=app_client.client_id)

    selected_content = [item for item in sample_content if item['content_type'] == 'link']
    assert len(selected_content) > 0
    
    content = selected_content[0]
    response = fb.post_content(
        content=content['content'],
        content_type=content['content_type'],
        caption=content.get('caption', ''),
        publish_now=True,
        comments=content.get('comments', [])
    )
    assert isinstance(response, dict)
    assert 'id' in response

def t_post_id_validity(db, app_client, app_tenant):
    page_id = app_client.client_id
    story_fbid = "1270701874727772"  # must be STORY_FBid
    access_token = app_client.page_access_token

    # logger.info(f'Page_access_token: {access_token}')

    graph_id = f"{page_id}_{story_fbid}"
    fb_url = (
        f"https://graph.facebook.com/v24.0/{graph_id}"
        f"?fields=id,permalink_url"
        f"&access_token={access_token}"
    )

    response = requests.get(fb_url)
    response_data = response.json()

    # Assertions
    assert "error" not in response_data, response_data
    assert "id" in response_data
    assert response_data["id"] == graph_id
    assert "permalink_url" in response_data

    logger.info(f"Post validation response: {response_data}")

def t_post_id_posting(db, app_client, app_tenant):
    fb = AutomateFacebookPost(page_id=app_client.client_id)

    # history = app_client.media_history
    # assert len(history) > 0
    # content = history[0]  # use the first media from history
    response = fb.post_content(
        content='1270701874727772',
        content_type='content_id',
        caption='Take a look at how you can use Smart Applicant to streamline your hiring process once again! #SmartApplicant #HiringMadeEasy',
        publish_now=True,
        comments=['This is a great tool for recruiters!', 'Loving the features of Smart Applicant.']
    )
    assert isinstance(response, dict)
    assert 'id' in response

def t_post_scheduling(db, app_client, app_tenant):
    schedule_facebook_post()
    assert True
   