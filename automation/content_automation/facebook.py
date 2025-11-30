from django.conf import settings
import requests
import logging
import time
from automation.models import Tenant
import random
from api.email_service import EmailService

logger = logging.getLogger(__name__)

class AutomateFacebookPost:
    __post_url = "https://graph.facebook.com/v24.0/page_id/"
    __page_access_token = ""
    __business_info: Tenant = None

    def __init__(self, page_id):
        self.page_id = page_id
        self.__page_access_token = settings.PAGE_DATA.get(page_id, {}).get("accees_token", "")
        self.__post_url = self.__post_url.replace("page_id", str(page_id))
        self.__business_info = Tenant.objects.filter(fb_page_id=page_id).first()
        if not self.__business_info:
            logger.warning(f"No business info found for page_id: {page_id}")
            raise ValueError("Invalid page_id or business info not found. Ensure the business that owns this page is registered with us.")
        if not self.__page_access_token:
            logger.warning(f"No access token found for page_id: {page_id}")
            raise ValueError("Access token not found for the given page_id.")
    
    def __get_business_details(self):
        return self.__business_info.business_details or {}
    
    def __send_email(self, text, email):
        email_service = EmailService(
            subject='Facebook Post Automation Report',
            to_emails=[email],
            template_name='emails/notification.html',
            context={
                'title': "Facebook Post Automation Notification",
                'text': text
            },
            from_email="Smart Applicant <support@smartapplicant.net>"
        )
        email_service.send_email()
    
    def __create_prompt_for_content_generation(self):
        business_details = self.__get_business_details()
        # prompt = (
        #     f"You are a skilled social media content creator for {self.__business_info.name}. "
        #     "Generate 6 Facebook posts for today: 3 text posts, 2 link posts (with caption), and 1 image post (with caption). "
        #     "Each post must be unique, engaging, and relevant to the business, with at least two hashtags. "
        #     "Keep tone friendly, professional, and appealing to Facebook users. "
        # )

        # if business_details:
        #     prompt += "Business details for context:\n"
        #     for key, value in business_details.items():
        #         prompt += f"- {key}: {value}\n"

        # prompt += (
        #     "Return output as a JSON list of dictionaries, each having:\n"
        #     '{"content": "<text or base64 image>", "caption": "<caption or empty>", "content_type": "text|link|image"}'
        # )
        prompt = (
            f"You are a skilled social media content creator for {self.__business_info.name}. "
            "Generate 6 Facebook posts for today: 3 text posts, 2 link posts (with caption), and 1 image post (with caption). "
            "Each post must be unique, engaging, and relevant to the business, with at least two hashtags. "
            "Keep tone friendly, professional, and appealing to Facebook users. "
            "You must not include personal information of the business owner or employees in the posts. "
        )

        if business_details:
            prompt += "Business details for context:\n"
            for key, value in business_details.items():
                prompt += f"- {key}: {value}\n"

        prompt += (
            "You are to create content focussing on the resume builder service ONLY for this business. "
            "Return output as a JSON list of dictionaries, with the following structures:\n"
            'Text content type - {"content": "<text>", "caption": "<empty>", "content_type": "text"}\n'
            'Link content type - {"content": "<url>", "caption": "<Text to encourage users to click the url>", "content_type": "link"}\n'
            'Text content type - {"content": "<image generation prompt>", "caption": "<Text to be posted with the image>", "content_type": "image"}'
        )

        return prompt
    
    def __get_media_history(self):
        media_history = self.__business_info.media_history or {}
        if media_history:
            return media_history.get('facebook', [])
        return []
    def __get_evergreen_content(self):
        evergreen_content = self.__business_info.evergreen_content or []
        return evergreen_content
    
    def __add_to_media_history(self, media_id, caption=""):
        media_history = self.__get_media_history()
        media_history.append({
            "id": media_id,
            "caption": caption
        })
        # keep only last 50 entries
        media_history = media_history[-50:]
        all_media_history = self.__business_info.media_history or {}
        all_media_history['facebook'] = media_history
        self.__business_info.media_history = all_media_history
        self.__business_info.save(update_fields=["media_history"])
    
    def __create_fallback_posts(self):
        media_history = self.__get_media_history()
        evergreen_content = self.__get_evergreen_content()

        # get two random media_history and 4 random evergreen content
        media_history = random.sample(media_history, min(2, len(media_history)))
        evergreen_content = random.sample(evergreen_content, min(4, len(evergreen_content)))

        fallback_posts = []
        for item in evergreen_content:
            fallback_posts.append({
                "content": item,
                "caption": "",
                "content_type": "text"
            })
        for item in media_history:
            fallback_posts.append({
                "content": item["id"],
                "caption": item.get("caption", ""),
                "content_type": "content_id"
            })
        return fallback_posts[:6]
    
    def get_fallback_posts(self):
        fallback_posts = self.__create_fallback_posts()
        if len(fallback_posts) < 6:
            logger.error("Not enough fallback content available for Facebook posts.")
            return []
        return fallback_posts
    
    def get_content_prompt(self):
        custom_prompt = self.__business_info.custom_prompts or {}
        return custom_prompt.get("facebook") or self.__create_prompt_for_content_generation()

    def get_schedule_times(self):
        schedule_times = self.__business_info.content_schedule_times or {}
        if not schedule_times or "facebook" not in schedule_times or len(schedule_times.get("facebook", [])) < 6:
            logger.info("Using default Facebook schedule times.")
            return [7, 9, 12, 15, 18, 21]
        return schedule_times.get("facebook", [])
    
    def comment_on_post(self, post_id: str, messages: list):
        """
        Adds a comment to a Facebook Page post.
        """
        GRAPH_URL = self.__post_url.replace("/page_id/", "")
        url = f"{GRAPH_URL}/{post_id}/comments"
        if messages:
            for comment in messages:
                payload = {
                    "message": comment,
                    "access_token": self.__page_access_token
                }
                response = requests.post(url, data=payload)
                if response.status_code > 299:
                    self.__send_email(f"Facebook Post Comment Action Failed: {response.text}", "zinando2000@gmail.com")
                time.sleep(1)
        return
    
    def like_post(self, post_id: str):
        """
        Adds a 'Like' reaction to a Facebook Page post.
        Note: Only the basic 'LIKE' works; other reactions aren't supported.
        """
        GRAPH_URL = self.__post_url.replace("/page_id/", "")
        url = f"{GRAPH_URL}/{post_id}/likes"
        payload = {
            "access_token": self.__page_access_token
        }

        response = requests.post(url, data=payload)
        if response.status_code > 299:
            self.__send_email(f"Facebook Post Like Action Failed: {response.text}", "zinando2000@gmail.com")
        return response.json()
    
    def post_content(self, content, caption, content_type="text", publish_now=True, comments:list=[], scheduled_time=None):
        if content_type == "text":
            self.__post_text_content(content, publish_now, scheduled_time, comments)
        elif content_type == "image":
            # check if content is bytes or URL
            if isinstance(content, (bytes, bytearray)):
                self.__post_image_bytes_content(content, caption, publish_now=publish_now, scheduled_time=scheduled_time)
            else:
                self.__post_image_url_content(content, caption, publish_now=publish_now, scheduled_time=scheduled_time)
        elif content_type == "link":
            self.__post_link_content(content, caption, publish_now=publish_now, scheduled_time=scheduled_time)
        elif content_type == "content_id":
            self.__post_content_id(content, caption, publish_now=publish_now, scheduled_time=scheduled_time)
        else:
            logger.error(f"Unsupported content type: {content_type}")
        
        return
        
    def __post_text_content(self, text, publish_now=True, scheduled_time=None, comments:list=[]):
        if scheduled_time and not publish_now:
            payload = {
                "message": text,
                "published": False,
                "scheduled_publish_time": scheduled_time,
                "access_token": self.__page_access_token
            }
        else:
            payload = {

                "message": text,
                "access_token": self.__page_access_token
            }
        # Here you would typically use requests.post to send the payload
        logger.info(f"Posting text content: {payload}")
        response = requests.post(f'{self.__post_url}feed', data=payload)
        if response.status_code == 200:
            logger.info(f"Successfully posted text content: {response.json()}")
            post_id = response.json()['id']

            # like post 
            self.like_post(post_id)

            # comment on post 
            self.comment_on_post(post_id, comments)
        else:
            logger.error(f"Failed to post text content: {response.text}")
    
    def __post_image_url_content(self, image_url, caption="", publish_now=True, scheduled_time=None):
        if scheduled_time and not publish_now:
            payload = {
                "url": image_url,
                "caption": caption,
                "published": False,
                "scheduled_publish_time": scheduled_time,
                "access_token": self.__page_access_token
            }
        else:
            payload = {
                "url": image_url,
                "caption": caption,
                "access_token": self.__page_access_token
            }
        # Here you would typically use requests.post to send the payload
        response = requests.post(f'{self.__post_url}photos', data=payload)

        if response.status_code == 200:
            parsed_json = response.json()
            self.__add_to_media_history(parsed_json.get("id"), caption)
            logger.info(f"Successfully posted media content: {response.json()}")
        else:
            logger.error(f"Failed to post media content: {response.text}")
    
    def __post_image_bytes_content(self, image_bytes, caption="", publish_now=True, scheduled_time=None):
        
        filename = f"fb_image_{int(time.time())}.jpg"
        files = {
            'source': (filename, image_bytes, 'image/jpeg')
        }

        if scheduled_time and not publish_now:
            payload = {
                "caption": caption,
                "published": False,
                "scheduled_publish_time": scheduled_time,
                "access_token": self.__page_access_token
            }
        else:
            payload = {
                "caption": caption,
                "access_token": self.__page_access_token
            }

        response = requests.post(f'{self.__post_url}photos', files=files, data=payload)

        if response.status_code == 200:
            parsed_json = response.json() 
            self.__add_to_media_history(parsed_json.get("id"), caption)
            logger.info(f"Successfully posted media content: {response.json()}")
        else:
            logger.error(f"Failed to post media content: {response.text}")
    
    def __post_link_content(self, link, caption="", publish_now=True, scheduled_time=None):
        if scheduled_time and not publish_now:
            payload = {
                "message": caption,
                "link": link,
                "published": False,
                "scheduled_publish_time": scheduled_time,
                "access_token": self.__page_access_token
            }
        else:
            payload = {
                "message": caption,
                "link": link,
                "access_token": self.__page_access_token
            }
        # Here you would typically use requests.post to send the payload
        logger.info(f"Posting text content: {payload}")
        response = requests.post(f'{self.__post_url}feed', data=payload)
        if response.status_code == 200:
            logger.info(f"Successfully posted text content: {response.json()}")
        else:
            logger.error(f"Failed to post text content: {response.text}")
    
    def __post_content_id(self, content_id, caption="", publish_now=True, scheduled_time=None):
        if scheduled_time and not publish_now:
            payload = {
                "attached_media": [{"media_fbid": content_id}],
                "message": caption,
                "published": False,
                "scheduled_publish_time": scheduled_time,
                "access_token": self.__page_access_token
            }
        else:
            payload = {
                "attached_media": [{"media_fbid": content_id}],
                "message": caption,
                "access_token": self.__page_access_token
            }
        # Here you would typically use requests.post to send the payload
        logger.info(f"Posting content by ID: {payload}")
        response = requests.post(f'{self.__post_url}feed', data=payload)
        if response.status_code == 200:
            logger.info(f"Successfully posted content by ID: {response.json()}")
        else:
            logger.error(f"Failed to post content by ID: {response.text}")
    