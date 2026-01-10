import os
import requests
from api.ai import get_structured_data_from_gemini
from django.conf import settings
from automation.models import AutomatedClients
import uuid
from moviepy import (
    VideoFileClip,
    ImageClip,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
    concatenate_videoclips
)

TEMP_DIR = "temp_assets"
os.makedirs(TEMP_DIR, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920


def download(url):
    filename = os.path.join(TEMP_DIR, str(uuid.uuid4()))
    r = requests.get(url)
    ext = url.split("?")[0].split(".")[-1]
    filename = f"{filename}.{ext}"
    with open(filename, "wb") as f:
        f.write(r.content)
    return filename


class VideoGenerator:

    def __init__(self, video_plan:dict=None, page_id:str=None):
        self.video_plan = video_plan
        self.page_id = page_id
        if not video_plan and not page_id:
            raise ValueError("Either video_plan or page_id must be provided")
        if not video_plan and page_id:
            # Placeholder for fetching video plan by page_id
            self.video_plan = self.fetch_video_plan(page_id)
        if not self.video_plan:
            raise ValueError("Video plan could not be determined")
        self.validate_video_plan()
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        self.clips = []
    
    def validate_video_plan(self):
        """Checks if video plan has required fields"""
        required_keys = {"media_type", "caption", "comments", "scenes"}
        if not all(key in self.video_plan for key in required_keys):
            raise ValueError("Video plan is missing required keys")
        if self.video_plan["media_type"] != "video":
            raise ValueError("Video plan media_type must be 'video'")
        if not isinstance(self.video_plan["scenes"], list) or len(self.video_plan["scenes"]) == 0:
            raise ValueError("Video plan must contain at least one scene")
        for scene in self.video_plan["scenes"]:
            scene_keys = {"media_type", "url", "overlay_text", "voice_over_text", "duration", "transition", "fade_in", "fade_out", "animation", "background_url", "background_music_url"}
            if not all(key in scene for key in scene_keys):
                raise ValueError("Each scene is missing required keys")
    
    def fetch_video_plan(self, page_id):
        # Get client by page_id
        try:
            client = AutomatedClients.objects.get(page_id=page_id)
        except AutomatedClients.DoesNotExist:
            raise ValueError("Client with given page_id does not exist")
        business_info = client.business_details
        if not business_info:
            raise ValueError("Business details are missing for the client")
        
        # check if has at least 10 assets: including audio and images/videos
        assets = client.business_assets or []
        if len(assets) < 10:
            raise ValueError("Not enough business assets to create video plan")
        assets = "\n".join(assets)
        if not ("audio" in assets or "music" in assets) or not any(ext in assets for ext in [".jpg", ".png", ".mp4", ".mov"]):
            raise ValueError("Assets must include at least one audio and one image/video file")
        system_prompt = """
        You are a professional advertising creative director and video scriptwriter.

        Your job is to generate a high-converting short-form vertical video ad plan for Facebook Reels using ONLY the provided business information and available assets.

        You must not invent or assume any asset.  
        You must only use the assets provided in the asset list.

        Your output must be valid JSON matching the schema below.
        No commentary. No explanations. No markdown.
        """.strip()
        prompt = f"""
                {system_prompt}

                BUSINESS INFORMATION:
                {business_info}

                AVAILABLE ASSETS:
                {assets}

                Create a 30-second vertical video ad (9:16) for Facebook Reels that:
                - Highlights the business’s main products or services
                - Creates emotional engagement
                - Explains the benefit
                - Ends with a clear call-to-action

                Use multiple scenes.
                Each scene must be 10 seconds long or less.
                Total duration must be between 28 and 32 seconds.

                Use a mix of images and videos if available.

                You must output a JSON object in the following format:

                {{
                "media_type": "video",
                "caption": "str - used to post along with the video on social media",
                "comments": ["str", "str", "4 to 6 comments to post along with the video on social media to set the tone for engagement"],
                "scenes": [
                    {{
                    "media_type": "image | video",
                    "url": "string (must come from available assets)",
                    "overlay_text": "string",
                    "voice_over_text": "string (spoken narration text) that will be converted to audio via TTS",
                    "duration": number (seconds),
                    "transition": "fade | slide | none",
                    "fade_in": number (seconds),
                    "fade_out": number (seconds),
                    "animation": "zoom_in | pan | none",
                    "background_url": "string or null - image from assets",
                    "background_music_url": "string or null - must come from url"
                    }},
                    ...
                ]
                }}

                Rules:
                - Use only URLs from the available assets list.
                - Overlay text must be short, bold, and readable on mobile.
                - Voice over should sound natural and persuasive.
                - Use the same background music across all scenes if available.
                - Do not leave fields blank.
                - Do not add extra keys.
                - Output only valid JSON.

        """.strip()
        return get_structured_data_from_gemini(prompt)

    def make_scene(self, scene):
        media_path = download(scene["url"])

        # Load image or video
        if scene["media_type"] == "image":
            base = ImageClip(media_path).set_duration(scene["duration"])
        else:
            base = VideoFileClip(media_path).subclip(0, scene["duration"])

        # Resize to vertical
        base = base.resize(height=HEIGHT)
        if base.w < WIDTH:
            base = base.resize(width=WIDTH)

        base = base.crop(x_center=base.w/2, y_center=base.h/2, width=WIDTH, height=HEIGHT)

        # Zoom animation
        if scene["animation"] == "zoom_in":
            base = base.fx(lambda clip: clip.resize(lambda t: 1 + 0.03 * t))

        # Text overlay
        txt = TextClip(
            scene["overlay_text"],
            fontsize=60,
            color="white",
            font="Arial-Bold",
            size=(900, None),
            method="caption"
        ).set_duration(scene["duration"]).set_position(("center", "bottom"))

        # Voice over
        if scene.get("voice_over_text"):
            voice_path = download(scene["voice_over_text"])
            voice = AudioFileClip(voice_path)
            base = base.set_audio(voice)

        # Music
        if scene.get("background_music_url"):
            music_path = download(scene["background_music_url"])
            music = AudioFileClip(music_path).volumex(0.2)
            base = base.set_audio(base.audio.set_duration(base.duration).fx(lambda a: a.audio_fadeout(1)).set_start(0).fx(lambda a: a) if base.audio else music)

        final = CompositeVideoClip([base, txt])

        if scene.get("fade_in"):
            final = final.fadein(scene["fade_in"])
        if scene.get("fade_out"):
            final = final.fadeout(scene["fade_out"])

        return final

    def render(self, output="final.mp4"):
        for scene in self.video_plan["scenes"]:
            clip = self.make_scene(scene)
            self.clips.append(clip)

        video = concatenate_videoclips(self.clips, method="compose")
        video.write_videofile(output, fps=30)

        # Cleanup
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))

        return output
