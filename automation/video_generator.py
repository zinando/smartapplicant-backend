import os
import requests
from api.ai import get_structured_data_from_gemini, try_call_tts
from django.conf import settings
from automation.models import AutomatedClients
import uuid
from urllib.parse import urlparse, unquote, parse_qs
from moviepy.video.fx import FadeIn, FadeOut, Resize
from moviepy.audio.fx import AudioFadeOut, AudioFadeIn, MultiplyVolume
import cv2
import numpy as np
from moviepy import (
    VideoFileClip,
    ImageClip,
    TextClip,
    CompositeVideoClip,
    CompositeAudioClip,
    AudioFileClip,
    concatenate_videoclips,
    vfx, afx
)

TEMP_DIR = "temp_assets"
os.makedirs(TEMP_DIR, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920

is_base_open = False
is_voice_open = False
base = None
voice = None

def gaussian_blur(clip, sigma=25):
    return clip.image_transform(
        lambda frame: cv2.GaussianBlur(frame, (0, 0), sigma)
    )

def fit_to_vertical(base, WIDTH, HEIGHT):
    # Background (blurred fill)
    bg = base.with_effects([vfx.Resize(width=WIDTH)])
    if bg.h < HEIGHT:
        bg = bg.with_effects([vfx.Resize(height=HEIGHT)])
    bg = gaussian_blur(bg, sigma=30)

    # Foreground (main video scaled to fit)
    fg = base.with_effects([vfx.Resize(height=HEIGHT)])
    if fg.w < WIDTH:
        fg = fg.with_effects([vfx.Resize(width=WIDTH)])

    return CompositeVideoClip(
        [bg, fg.with_position("center")],
        size=(WIDTH, HEIGHT)
    )

def extract_drive_id(url):
    if "/file/d/" in url:
        return url.split("/file/d/")[1].split("/")[0]
    if "id=" in url:
        return parse_qs(urlparse(url).query)["id"][0]
    raise ValueError("Invalid Google Drive URL")

def download(url, media_type="image"):
    os.makedirs(TEMP_DIR, exist_ok=True)

     # Convert Google Drive links
    if "drive.google.com" in url:
        file_id = extract_drive_id(url)
        url = f"https://drive.google.com/uc?export=download&id={file_id}"


    r = requests.get(url, stream=True)
    r.raise_for_status()

    # Try to get filename from headers
    filename = None
    cd = r.headers.get("Content-Disposition")
    if cd and "filename=" in cd:
        filename = cd.split("filename=")[-1].strip("\"'")

    # Fallback: guess from URL
    if not filename:
        path = urlparse(url).path
        filename = os.path.basename(path)
        if not filename:
            filename = str(uuid.uuid4())

    filename = unquote(filename)

    # If no extension, add default
    if "." not in filename:
        if media_type == "video":
            filename += ".mp4"
        elif media_type == "audio":
            filename += ".mp3"
        else:
            filename += ".jpg"

    full_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}_{filename}")

    with open(full_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    return full_path


class VideoGenerator:

    def __init__(self, page_id:str, video_plan:dict=None):
        self.video_plan = video_plan
        self.page_id = page_id
        if not page_id:
            raise ValueError("page_id is required")
        if not video_plan:
            # Placeholder for fetching video plan by page_id
            self.video_plan = self.fetch_video_plan(page_id)
        if not self.video_plan:
            raise ValueError("Video plan could not be determined")
        self.validate_video_plan()
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        self.clips = []
        self.content_schedule_times = [7, 8, 9, 10, 11]
        self.page_content_schedule_times = []
    
    def validate_video_plan(self):
        """Checks if video plan has required fields"""
        required_keys = {"media_type", "caption", "comments", "scenes", "background_music_url"}
        if not all(key in self.video_plan for key in required_keys):
            raise ValueError("Video plan is missing required keys")
        if self.video_plan["media_type"] != "video":
            raise ValueError("Video plan media_type must be 'video'")
        if not isinstance(self.video_plan["scenes"], list) or len(self.video_plan["scenes"]) == 0:
            raise ValueError("Video plan must contain at least one scene")
        for scene in self.video_plan["scenes"]:
            scene_keys = {"media_type", "url", "overlay_text", "voice_over", "duration", "transition", "fade_in", "fade_out", "animation", "background_url"}
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
        
        if client.content_schedule_times:
            self.page_content_schedule_times = client.content_schedule_times
        
        # check if has at least 10 assets: including audio and images/videos
        assets = client.business_assets or []
        if len(assets) < 10:
            raise ValueError("Not enough business assets to create video plan")
        assets = "\n".join(assets)
        if not ("audio" in assets or "music" in assets) or not any(ext in assets for ext in [".jpg", ".PNG", ".jpeg", ".png", ".mp4", ".mov"]):
            raise ValueError("Assets must include at least one audio and one image/video file")
        
        # compose prompt for Gemini
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
                "background_music_url": "string or null - must come from available assets",
                "video_cover_url": "string or null - must come from available assets",
                "watermark": "string - logo image URL from assets if there is one, otherwise business name",
                "scenes": [
                    {{
                    "media_type": "image | video",
                    "url": "string (must come from available assets)",
                    "overlay_text": "string",
                    "voice_over": "string (spoken narration text) that will be converted to audio via TTS",
                    "duration": number (seconds),
                    "transition": "fade | slide | none",
                    "fade_in": number (seconds),
                    "fade_out": number (seconds),
                    "animation": "zoom_in | pan | none",
                    "background_url": "string or null - image from assets"
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
        global is_base_open, is_voice_open, base, voice

        try:
            # Download media
            if scene["media_type"] == "video":
                media_path = download(scene["url"], media_type="video")
                base = VideoFileClip(media_path).with_duration(0, scene["duration"])
                is_base_open = True
            else:
                media_path = download(scene["url"], media_type="image")
                base = ImageClip(media_path).with_duration(scene["duration"])

            # Resize to vertical
            base = fit_to_vertical(base, WIDTH, HEIGHT)
            
            # Zoom animation
            if scene["animation"] == "zoom_in":
                base = base.with_effects([vfx.Resize(lambda t: 1 + 0.03 * t)])

            # Text overlay
            txt = TextClip(
                text=scene["overlay_text"],
                font_size=60,
                bg_color=(0,0,0),
                color="white",
                # font="Arial-Bold",
                size=(900, None),
                method="caption"
            ).with_duration(scene["duration"]).with_position(("center", 0.78), relative=True)
            txt = txt.with_opacity(0.5)

            # Voice over
            if scene.get("voice_over"):
                voice_path, status = try_call_tts(scene["voice_over"])
                if voice_path:
                    voice = AudioFileClip(voice_path)
                    base = base.with_audio(voice)
                    is_voice_open = True
                else:
                    print(f"Failed to generate voice over for scene: {scene['voice_over']}")

            final = CompositeVideoClip([base, txt])

            # Fades
            if scene.get("fade_in"):
                final = final.with_effects([FadeIn(scene["fade_in"])])

            if scene.get("fade_out"):
                final = final.with_effects([FadeOut(scene["fade_out"])])

            return final
        except Exception as e:
            if is_base_open:
                base.close()
            if is_voice_open:
                voice.close()
            print(f"Error creating scene for URL {scene['url']}: {e}")
            raise e
    
    def make_cover(self, cover_url):
        # ownload the cover image
        cover = download(cover_url, media_type="image")
        cover_obj = ImageClip(cover).with_duration(1.2)
        cover_obj = cover_obj.with_effects([vfx.Resize(height=HEIGHT)])
        if cover_obj.w < WIDTH:
            cover_obj = cover_obj.with_effects([vfx.Resize(width=WIDTH)])
        return cover_obj
    
    def make_watermark(self, input:str, duration:float=10):
        """Creates a watermark clip from text or logo image"""
        if input.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) or any(s in input for s in ["https://", "http://", "www.", "drive.google.com"]):
            # Treat as image URL
            logo_path = download(input, media_type="image")
            watermark = (ImageClip(logo_path)
                         .with_duration(duration)
                         .with_effects([vfx.Resize(height=100)])
                         .with_position(("right", "top"))
                        #  .with_margin(right=10, top=10)
                         .with_opacity(0.7))
        else:
            # Treat as text
            watermark = (TextClip(text=input, font_size=24, color='white', bg_color='black')
                         .with_duration(duration)
                         .with_position(("right", "top"))
                        #  .with_margin(right=10, top=10)
                         .with_opacity(0.7))
        watermark = watermark.with_position(("center", 0.78), relative=True)
        return watermark

    def render(self):
        output = f"temp_media/{uuid.uuid4()}_final.mp4"
        global is_base_open, is_voice_open, base, voice
        open_audio_clips = []
        message = ""

        try:
            # Build scenes
            for scene in self.video_plan["scenes"]:
                clip = self.make_scene(scene)
                self.clips.append(clip)

            # add cover image at start
            cover_clip = self.make_cover(self.video_plan.get("video_cover_url", self.video_plan["scenes"][0]["url"]))
            self.clips.insert(0, cover_clip)

            video = concatenate_videoclips(self.clips, method="compose")

            # add watermark if specified
            if self.video_plan.get("watermark"):
                watermark = self.make_watermark(self.video_plan["watermark"], duration=video.duration)
                video = CompositeVideoClip([video, watermark])

            # Background music
            music = None
            if self.video_plan.get("background_music_url"):
                music_path = download(self.video_plan["background_music_url"], media_type="audio")
                music = AudioFileClip(music_path)
                open_audio_clips.append(music)

                music = music.with_effects([MultiplyVolume(0.2)])
                music = music.subclipped(0, video.duration)

                if video.audio:
                    final_audio = CompositeAudioClip([video.audio, music])
                else:
                    final_audio = music

                video = video.with_audio(final_audio)

            # Render
            video.write_videofile(output, fps=24, codec="libx264", audio_codec="aac")

            # Cleanup ffmpeg resources
            if video.audio:
                video.audio.close()

            if music:
                music.close()

            for clip in self.clips:
                try:
                    clip.close()
                except:
                    pass
            
            if is_base_open:
                base.close()
            if is_voice_open:
                voice.close()

            video.close()

            # Delete temp assets
            for f in os.listdir(TEMP_DIR):
                os.remove(os.path.join(TEMP_DIR, f))
            
            message = "Video rendered successfully"
        except Exception as e:
            print(f"Error rendering video: {e}")
            output = None
            message = str(e)

        return output, message