import pytest
from automation.content_automation.facebook import AutomateFacebookPost
import logging
from api.ai import get_structured_data_from_gemini
from automation.mydata import sample_content
from django.conf import settings
import requests
from django.utils import timezone
from automation.tasks import schedule_facebook_post
from automation.mydata import notes
from automation.ai_commands import subscribe_to_post_automation

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

def test_post_scheduling(db, app_client, app_tenant):
    schedule_facebook_post()
    assert True
def t_subscribe_to_post_automation(db, app_client, app_tenant):
    new_info = {
        'name': "Smart & Trendy Blitz",
        'email': "zinando2000@gmail.com",
        'type': "product seller",
        'description': "Smart & Trendy Blitz is a clothing retail store. We deal on high quality first grade second-hand clothes. We have clothes for all categories of buyers: male and female, kids, adults, fat and slim. We get new stocks every Monday of the week.",
        'how_to_use': "1. Join our whatsapp group via the link: https://chat.whatsapp.com/ER5UAeB7ZfHGN8TC30qDsV?mode=ems_copy_t 2. Lookout for daily updates on our latest stocks 3. Place private chat the admin with the image of your desired item(s) 4. Place order by making payment 5. Get your goods delievred to you.",
        'features': "1. Sweatshirts 2. Jeans 3. Office wears 4. Gowns 5. Crop tops 6. Boyfriend jeans 7. children party gowns 8. Pyngamas (night wears) 9. Chinos 10. t-shirts 11. Polos 12. Shorts 13. Joggers",
        'website': "",
        'address': "Suite 7 Divine Imperial Place, Opposite Makkah Eye Specialist Hospital, by Elebu junction, Akala Express, Ibadan, Oyo State, Nigeria",
        'business_contacts': "2347031104270 (call or WhatsApp)",
        'social_links': "1. Facebook: https://www.facebook.com/share/1DD242kn8q/",
        'services': "",
        'products': "1. Sweatshirts 2. Jeans 3. Office wears 4. Gowns 5. Crop tops 6. Boyfriend jeans 7. children party gowns 8. Pyngamas (night wears) 9. Chinos 10. t-shirts 11. Polos 12. Shorts 13. Joggers",
        'pricing': "Children wears - from N1500 upwards, Adult wears - from N3000 upwards",
        'image_links': "",
        'business_links': "",
        'secret_questions': "Q: Mother's maiden name? A: Isietu. Q: Best friend's name in Logiss (my secondary school)? A: Ikechukwu Nnadilim. Q: last primary school attended? A: Pioneer Primary School, Edenta, Awo-Idemili, Imo State.",
        'last_updated': timezone.now().strftime("%d-%m-%Y"),
        'notes': notes
    }
