# from django.conf import settings
from automation.models import AutomatedClients
import os
from api.email_service import EmailService
import logging
import requests
import random
from datetime import datetime, timezone
from automation.utils import to_facebook_timestamp
# import time

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v24.0"
CHUNK_SIZE = 1024 * 1024 * 4  # 4MB

class FacebookVideoUploader:
    __comment_url = "https://graph.facebook.com/v24.0/post_id/comments"
    __like_url = "https://graph.facebook.com/v24.0/post_id/likes"
    def __init__(self, page_id: str):
        self.page_id = page_id
        self.page_data = self._load_page_data()
        # print(f"Page Data: \n{self.page_data}")
        self.access_token = self.page_data["access_token"]
        self.video = self.page_data["video"]
        self.page_content_schedule_times = None

    # --------------------------------------------------
    # DB
    # --------------------------------------------------
    def _get_schedule_time(self):
        ideal_times = [9, 10, 11, 12, 13, 14]

        if self.page_content_schedule_times and isinstance(self.page_content_schedule_times, list):
            non_overlapping_times = [tym for tym in ideal_times if tym not in self.page_content_schedule_times]
            if non_overlapping_times:
                return random.choice(non_overlapping_times)
        return 

    def _load_page_data(self) -> dict:
        """
        Fetch page + video content from DB.
        This method MUST return everything needed to post.
        """
        page = AutomatedClients.objects.filter(client_id=self.page_id).first()

        if not page:
            raise ValueError(f"Client with client_id {self.page_id} not found.")
        
        if page.content_schedule_times:
            self.page_content_schedule_times = page.content_schedule_times
        
        # get video plan
        vp = page.saved_video_plan

        if not vp:
            raise ValueError("No video plan found.")

        if not vp.get("final_video_path"):
            raise ValueError(f"Video was not created")
        
        logger.info(f"Video plan with completed video found. PATH: {vp.get('final_video_path')}")

        return {
            "access_token": page.page_access_token,
            "video": {
                "path": vp.get("final_video_path"),
                "caption": vp.get("caption", ""),
                "schedule_time": self._get_schedule_time(),
                "comments": vp.get("comments"),
                "page_name": page.business_details.get("name", self.page_id),
                "email": page.business_details.get("email", "zinando2000@gmail.com")
            },
        }

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------
    def upload(self) -> dict:
        self._validate_video()

        response = self._upload_video()
        video_id = response.get("video_id")

        if not video_id:
            raise RuntimeError(f"Upload failed: {response}")
        
        self._send_email(f"Video has been posted to your facebook page: {self.video.get('page_name', self.page_id)}.\nVideo Caption: {self.video.get('caption', '')}.\nSchedule Time: {self.video.get('schedule_time', '')}th hour today.", self.video.get("email", "zinando2000@gmail.com"))

        # empty saved video plan
        client = AutomatedClients.objects.filter(client_id=self.page_id).first()
        client.saved_video_plan = None
        client.save(update_fields=["saved_video_plan"])
        return {
            "status": "success",
            "video_id": video_id,
        }

    # --------------------------------------------------
    # INTERNALS
    # --------------------------------------------------
    def _validate_video(self):
        path = self.video["path"]

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        if not path.lower().endswith(".mp4"):
            raise ValueError("Facebook requires MP4 videos")

    def _upload_video(self) -> dict:
        path = self.video["path"]
        file_size = os.path.getsize(path)

        # -------------------------------
        # START
        # -------------------------------
        start_url = f"{GRAPH_API_BASE}/{self.page_id}/videos"
        start_payload = {
            "access_token": self.access_token,
            "upload_phase": "start",
            "file_size": file_size,
        }

        r = requests.post(start_url, data=start_payload)
        r.raise_for_status()
        session = r.json()

        upload_session_id = session["upload_session_id"]
        video_id = session["video_id"]
        start_offset = int(session["start_offset"])
        end_offset = int(session["end_offset"])

        # -------------------------------
        # TRANSFER
        # -------------------------------
        with open(path, "rb") as f:
            while start_offset < end_offset:
                f.seek(start_offset)
                chunk = f.read(CHUNK_SIZE)

                transfer_payload = {
                    "access_token": self.access_token,
                    "upload_phase": "transfer",
                    "upload_session_id": upload_session_id,
                    "start_offset": start_offset,
                }

                files = {
                    "video_file_chunk": chunk
                }

                r = requests.post(start_url, data=transfer_payload, files=files)
                r.raise_for_status()
                result = r.json()

                start_offset = int(result["start_offset"])
                end_offset = int(result["end_offset"])

        # -------------------------------
        # FINISH
        # -------------------------------
        finish_payload = {
            "access_token": self.access_token,
            "upload_phase": "finish",
            "upload_session_id": upload_session_id,
            "description": self.video["caption"],
        }

        # Scheduling (Facebook requires UNIX timestamp + published=false)
        schedule_time = self.video.get("schedule_time")
        now = datetime.now(timezone.utc)
        if schedule_time and isinstance(schedule_time, int):
            schedule_time = schedule_time if (now.hour + 1) < schedule_time < 24 else None

            finish_payload.update({
                "published": "false" if schedule_time else "true",
                "scheduled_publish_time": None if not schedule_time else to_facebook_timestamp(schedule_time),
            })

        r = requests.post(start_url, data=finish_payload)
        r.raise_for_status()

        # delete video file 
        self._delete_video_file(path)

        return {
            "video_id": video_id,
            "status": "uploaded",
        }
    
    def _delete_video_file(self, path):
        # Delete temp assets
        os.remove(path)
    
    def _add_comments(self, post_id: str):
        comments = self.video.get("comments", [])

        for comment in comments:
            url = f"{GRAPH_API_BASE}/{self.page_id}_{post_id}/comments"
            data = {
                "access_token": self.access_token,
                "message": comment,
            }

            r = requests.post(url, data=data)
            r.raise_for_status()
    
    def _like_post(self, post_id: str):
        """
        Adds a 'Like' reaction to a Facebook Page post.
        Note: Only the basic 'LIKE' works; other reactions aren't supported.
        """
        url = self.__like_url.replace("post_id", f"{self.page_id}_{post_id}")
        payload = {
            "access_token": self.access_token
        }

        response = requests.post(url, data=payload)
        if response.status_code > 299:
            self._send_email(f"Facebook Post Like Action Failed: {response.text}", "zinando2000@gmail.com")
        return response.json()
    
    def _send_email(self, text, email):
        # print(f"Recipient email: {email}")
        # return
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

    def _get_post_id(self, video_id):
        url = f"https://graph.facebook.com/v24.0/{video_id}"
        params = {
            "fields": "post_id",
            "access_token": self.access_token
        }

        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json().get("post_id")
    

