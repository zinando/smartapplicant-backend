from django.conf import settings
import requests
import logging
import time
from automation.models import Tenant, AutomatedClients
import random
from api.email_service import EmailService
from automation.utils import to_facebook_timestamp

logger = logging.getLogger(__name__)

class AutomateFacebookPost:
    __post_url = "https://graph.facebook.com/v24.0/page_id/"
    __comment_url = "https://graph.facebook.com/v24.0/post_id/comments"
    __like_url = "https://graph.facebook.com/v24.0/post_id/likes"
    __page_access_token = ""
    __business_info: AutomatedClients = None

    def __init__(self, page_id):
        self.page_id = page_id
        self.__page_access_token = settings.PAGE_DATA.get(page_id, {}).get("accees_token", "")
        self.__post_url = self.__post_url.replace("page_id", str(page_id))
        # self.__business_info = Tenant.objects.filter(fb_page_id=page_id).first()
        self.__business_info = AutomatedClients.objects.filter(platform="facebook", client_id=page_id).first()
        if not self.__business_info:
            logger.warning(f"No business info found for page_id: {page_id}")
            raise ValueError("Invalid page_id or business info not found. Ensure the business that owns this page is registered with us.")
        if not self.__page_access_token:
            logger.warning(f"No access token found for page_id: {page_id}")
            raise ValueError("Access token not found for the given page_id.")
    
    def __get_business_details(self):
        return self.__business_info.business_details or {}
    
    def get_business_details(self):
        return self.__get_business_details()
    
    def __send_email(self, text, email):
        email_service = EmailService(
            subject='Facebook Post Automation Report',
            to_emails=[email],
            template_name='emails/notification.html',
            context={
                'title': "Facebook Post Automation Notification",
                'text': text
            },
            from_email="Smart Applicant <contact@smartapplicant.net>"
        )
        email_service.send_email()
    
    def send_email(self, text, email):
        self.__send_email(text, email)
    
    def __create_prompt_for_content_generation(self):
        business_details = self.__get_business_details()
        if not business_details:
            logger.warning("No business details found for content generation prompt.")
            return ""
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
        
        # prompt = (
        #     f"You are a skilled social media content creator for {self.__business_info.name}. "
        #     "Generate 6 Facebook posts for today: 3 text posts, 2 link posts (with caption), and 1 image post (with caption). "
        #     "Each post must be unique, engaging, and relevant to the business, with at least two hashtags. "
        #     "Keep tone friendly, professional, and appealing to Facebook users. "
        #     "For each post, create between 4 to 6 unique comments to further buttress the point of the post or to drive engagement. "
        #     "You are commenting as the post creator to encourage engagement and to add value to the post. "
        #     "You must not include personal information of the business owner or employees in the posts. "
        # )

        # if business_details:
        #     prompt += "Business details for context:\n"
        #     for key, value in business_details.items():
        #         prompt += f"- {key}: {value}\n"

        # prompt += (
        #     "You are to create content focussing on the resume builder service ONLY for this business. "
        #     "Return output as a JSON list of dictionaries, with the following structures:\n"
        #     'Text content type - {"content": "<text>", "caption": "<empty>", "content_type": "text", "comments": "<List of 4 or more unique text comments to buttress the post>"}\n'
        #     'Link content type - {"content": "<url>", "caption": "<Text to encourage users to click the url>", "content_type": "link","comments": "<List of 4 or more unique text comments to buttress the post>"}\n'
        #     'Text content type - {"content": "<image generation prompt>", "caption": "<Text to be posted with the image>", "content_type": "image", "comments": "<List of 4 or more unique text comments to buttress the post>"}'
        # )
        prompt = (
            f"You are a skilled social media content creator for {business_details.get('name', 'the business')}. "
            "Generate 6 Facebook posts for today: 4 text posts, 2 link posts (with caption). "
            "Each post must be unique, engaging, and relevant to the business, with at least two hashtags. "
            "Keep tone friendly, professional, and appealing to Facebook users. "
            "For each post, create between 4 to 6 unique comments to further buttress the point of the post or to drive engagement. "
            "You are commenting as the post creator to encourage engagement and to add value to the post. "
            "You must not include personal information of the business owner or employees in the posts. "
        )

        if business_details:
            prompt += "Business details for context:\n"
            for key, value in business_details.items():
                prompt += f"- {key}: {value}\n"

        prompt += (
            "Return output as a JSON list of dictionaries, with the following structures:\n"
            'Text content type - {"content": "<text>", "caption": "<empty>", "content_type": "text", "comments": "<List of 4 or more unique text comments to buttress the post>"}\n'
            'Link content type - {"content": "<url>", "caption": "<Text to encourage users to click the url>", "content_type": "link","comments": "<List of 4 or more unique text comments to buttress the post>"}'
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
        self.__business_info.media_history = media_history
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
    
    def make_a_test_post(self):
        content = """
        💼 Stop Guessing. Start Winning.

        We’ve all been there — staring at a blank resume, wondering what to write, what matters, and what might just cost us an interview.

        That’s why we built SmartApplicant
        — your AI-powered career companion that doesn’t just help you create a resume, but helps you sound confident, professional, and ready to impress.

        ✨ Intelligent suggestions
        ✨ ATS-friendly formatting
        ✨ AI-guided refinement — free to use when you keep it simple

        Over 1,300 job seekers have already landed interviews using SmartApplicant.
        Now it’s your turn. 🚀

        👉 Visit smartapplicant.net
        and start building your job-winning resume today.

        #SmartApplicant #CareerGrowth #ResumeTips #AIinRecruitment #JobSearch #LinkedInAfrica
        """
        caption = ""

        comments = [
            "Many users don’t realize how much a well-structured resume changes their job search. SmartApplicant is designed to remove the guesswork and present your strengths clearly and professionally. If you haven’t tried it yet, now is the best time to start. 🚀",
            "One of my favorite features is how SmartApplicant instantly rewrites weak bullet points into strong, results-driven statements. Most people struggle with how to phrase their achievements — the AI makes it effortless.",
            """
            Quick reminder: Recruiters spend less than 7 seconds scanning a resume.
            That’s why structure, clarity, and relevance matter.
            SmartApplicant helps job seekers fix these issues in minutes.""",
            """What part of resume writing do you struggle with the most —
            ✔ formatting
            ✔ writing achievements
            ✔ choosing the right words
            ✔ or knowing what to include/remove?

            I’d love to hear your thoughts 👇""",
            """If you’ve been applying for jobs without getting feedback, your resume may be the missing piece. SmartApplicant gives you fresh perspective, cleaner formatting, and more confidence.

            Try it for free at smartapplicant.net.""",
            """We built SmartApplicant because every job seeker deserves clarity, not confusion.
            Whether you’re a graduate, mid-career professional, or switching fields — a strong resume is your biggest advantage.

            Wishing everyone success in their next application! 💼✨"""
        ]

        self.post_content(
            content=content,
            caption=caption,
            content_type="text",
            publish_now=False,
            comments=comments,
            scheduled_time="1764831600"
        )
        return
    
    def get_fallback_posts(self):
        fallback_posts = self.__create_fallback_posts()
        if len(fallback_posts) < 6:
            logger.error("Not enough fallback content available for Facebook posts.")
            return []
        return fallback_posts
    
    def get_content_prompt(self):
        return self.__business_info.custom_prompt or self.__create_prompt_for_content_generation()

    def get_schedule_times(self):
        schedule_times = self.__business_info.content_schedule_times or {}
        if not schedule_times:
            return [7, 9, 12, 15, 18, 21]
        return schedule_times
    
    def comment_on_post(self, post_id: str, messages: list):
        """
        Adds a comment to a Facebook Page post.
        """
        url = self.__comment_url.replace("post_id", post_id)
        if messages:
            for comment in messages:
                payload = {
                    "message": comment,
                    "access_token": self.__page_access_token
                }
                response = requests.post(url, data=payload)
                logger.info(f'URL: {url} \nComment ID: {response.json()}')
                if response.status_code > 299:
                    self.__send_email(f"Facebook Post Comment Action Failed: {response.text}", "zinando2000@gmail.com")
                    break
                time.sleep(1)
        return
    
    def like_post(self, post_id: str):
        """
        Adds a 'Like' reaction to a Facebook Page post.
        Note: Only the basic 'LIKE' works; other reactions aren't supported.
        """
        url = self.__like_url.replace("post_id", post_id)
        payload = {
            "access_token": self.__page_access_token
        }

        response = requests.post(url, data=payload)
        if response.status_code > 299:
            logger.error(response.text)
            self.__send_email(f"Facebook Post Like Action Failed: {response.text}", "zinando2000@gmail.com")
        return response.json()
    
    def post_content(self, content, caption, content_type="text", publish_now=True, comments:list=[], scheduled_time=None):
        if content_type == "text":
            self.__post_text_content(content, publish_now, scheduled_time, comments)
        elif content_type == "image":
            # check if content is bytes or URL
            if isinstance(content, (bytes, bytearray)):
                self.__post_image_bytes_content(content, caption, publish_now=publish_now, scheduled_time=scheduled_time, comments=comments)
            else:
                self.__post_image_url_content(content, caption, publish_now=publish_now, scheduled_time=scheduled_time, comments=comments)
        elif content_type == "link":
            self.__post_link_content(content, caption, publish_now=publish_now, scheduled_time=scheduled_time, comments=comments)
        elif content_type == "content_id":
            self.__post_content_id(content, caption, publish_now=publish_now, scheduled_time=scheduled_time, comments=comments)
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
        
        response = requests.post(f'{self.__post_url}feed', data=payload)
        if response.status_code == 200:
            response_data = response.json()
            logger.info(f"Successfully posted text content: {response_data}")
            post_id = response_data['id']

            # like post 
            self.like_post(post_id)

            # comment on post 
            self.comment_on_post(post_id, comments)
        else:
            logger.error(f"Failed to post text content: {response.text}")
    
    def __post_image_url_content(self, image_url, caption="", publish_now=True, scheduled_time=None, comments=[]):
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
            logger.info(f"Successfully posted media content: {parsed_json}")
            post_id = parsed_json.get("id")

            # like post
            self.like_post(post_id)

            # comment on post
            self.comment_on_post(post_id, comments)
        else:
            logger.error(f"Failed to post media content: {response.text}")

    def __post_image_bytes_content(self, image_bytes, caption="", publish_now=True, scheduled_time=None, comments=[]):

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
            logger.info(f"Successfully posted media content: {parsed_json}")
            post_id = parsed_json.get("id")

            # like post
            self.like_post(post_id)

            # comment on post
            self.comment_on_post(post_id, comments)
        else:
            logger.error(f"Failed to post media content: {response.text}")

    def __post_link_content(self, link, caption="", publish_now=True, scheduled_time=None, comments=[]):
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
            response_data = response.json()
            post_id = response_data['id']
            logger.info(f"Successfully posted text content: {response.json()}")

            # like post
            self.like_post(post_id)

            # comment on post
            self.comment_on_post(post_id, comments)
        else:
            logger.error(f"Failed to post text content: {response.text}")
    
    def __post_content_id(self, content_id, caption="", publish_now=True, scheduled_time=None, comments=[]):
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
            response_data = response.json()
            post_id = response_data['id']
            logger.info(f"Successfully posted content by ID: {response_data}")

            # like post
            self.like_post(post_id)
            # comment on post
            self.comment_on_post(post_id, comments)
        else:
            logger.error(f"Failed to post content by ID: {response.text}")
    