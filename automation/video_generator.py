import os
import requests
from api.ai import get_structured_data_from_gemini, try_call_tts, get_structured_data_from_gemini_smart
from django.conf import settings
from automation.models import AutomatedClients
import uuid
import subprocess
from pathlib import Path
import json 
from urllib.parse import urlparse, unquote, parse_qs
from moviepy.video.fx import FadeIn, FadeOut, Resize
from moviepy.audio.fx import AudioFadeOut, AudioFadeIn, MultiplyVolume
import cv2
import re
import numpy as np
import textwrap
import shutil
import hashlib
from automation.helpers import save_cache, get_cache

# from automation.tasks import post_video_content_to_facebook
# from automation.content_automation.post_video import FacebookVideoUploader
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

DRIVE_VIEW_REGEX = re.compile(
    r"https://drive\.google\.com/(file/d/[^/]+/view|open\?id=[^&]+|uc\?id=[^&]+)"
)

# 1440 × 2640
# 1080 x 1920
WIDTH = 1440
HEIGHT = 2640

is_base_open = False
is_voice_open = False
base = None
voice = None

LOGO_CACHE_DIR = Path("logo_cache")
LOGO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

def has_audio(video_path:str):
    video_clip = None
    try:
        video_clip = VideoFileClip(str(video_path))
        has_audio = video_clip.audio is not None
    except Exception as e:
        print(str(e))
        has_audio = False
    finally:
        if video_clip:
            video_clip.close()
    return has_audio

def is_google_drive_view_link(url: str) -> bool:
    return bool(DRIVE_VIEW_REGEX.match(url))

def validate_url(url:str) ->bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return is_google_drive_view_link(url)

def gaussian_blur(clip, sigma=25):
    return clip.image_transform(
        lambda frame: cv2.GaussianBlur(frame, (0, 0), sigma)
    )

def run(cmd):
    subprocess.run(cmd, check=True)

def get_video_duration(path: str) -> float:
    """
    Returns video duration in seconds (float)
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "format=duration",
            "-of", "json",
            path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )

    data = json.loads(result.stdout)
    return float(data["format"]["duration"])

def get_audio_duration_from_video(path):
    result = subprocess.run(
        [
            "ffprobe", 
            "-v", "error",
            "-select_streams", "a:0", # Select the first audio stream
            "-show_entries", "stream=duration", # Get stream duration, not format duration
            "-of", "default=noprint_wrappers=1:nokey=1",
            path
        ],
        capture_output=True,
        text=True
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0

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

def get_media_duration(media_path, stream_type="v"):
    """
    Returns the duration of a media file in seconds (float).
    
    Parameters:
        media_path (str): Path to the media file (video/audio).
        stream_type (str): "v" for video, "a" for audio.
                           Defaults to "v" (video).
    
    Returns:
        float: Duration in seconds.
    """
    if stream_type not in ("v", "a"):
        raise ValueError("stream_type must be 'v' (video) or 'a' (audio)")

    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",                     # suppress logs
            "-select_streams", f"{stream_type}:0",  # first stream of given type
            "-show_entries", "format=duration",     # total duration
            "-of", "default=noprint_wrappers=1:nokey=1",
            media_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        return float(result.stdout.strip())
    except ValueError:
        # fallback: return 0 if duration not found
        return 0.0
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
        if isinstance(self.video_plan["watermark"], str):
            if not validate_url(self.video_plan["watermark"]):
                raise ValueError("watermark is not a valid url")
        if isinstance(self.video_plan["watermark"], dict):
            wmk_keys = {"text", "text_color", "font"}
            if not all(key in self.video_plan['watermark'] for key in wmk_keys):
                raise ValueError("Watermark is missing important keys")
        for scene in self.video_plan["scenes"]:
            scene_keys = {"media_type", "url", "overlay_text", "voice_over", "duration", "transition", "fade_in", "fade_out", "animation", "background_url"}
            if not all(key in scene for key in scene_keys):
                raise ValueError("Each scene is missing required keys")
            text_overlay = scene.get("overlay_text")
            if not text_overlay:
                raise ValueError("overlay_text not present")
            text_overlay_keys = {"text", "text_color", "font", "font_size"}
            if not all(key in text_overlay for key in text_overlay_keys):
                raise ValueError(f"{scene} is missing vital keys in its overlay_text value")
    
    def fetch_video_plan(self, page_id):
        # Get client by page_id
        try:
            client = AutomatedClients.objects.get(client_id=page_id)
        except AutomatedClients.DoesNotExist:
            raise ValueError(f"Client with page ID {page_id} does not exist")
        business_info = client.business_details
        if not business_info:
            raise ValueError("Business details are missing for the client")
        
        if client.content_schedule_times:
            self.page_content_schedule_times = client.content_schedule_times
        
        # check if there is existing video plan
        if client.saved_video_plan:
            return client.saved_video_plan

        # check if cliet has at least 10 assets: including audio and images/videos
        assets = client.business_assets or []
        if len(assets) < 10:
            raise ValueError("Not enough business assets to create video plan")
        assets = "\n".join(assets)
        if not ("audio" in assets or "music" in assets) or not any(key in assets for key in ["image", "video"]): #or not any(ext in assets for ext in [".jpg", ".PNG", ".jpeg", ".png", ".mp4", ".mov"]):
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
                Each scene must be at least 5 seconds long and at most 10 seconds long.
                Total duration must be between 28 and 32 seconds.

                Use a mix of images and videos if available.
                use the asset descriptions to understand the content of each assset, and make a decision on which asset would be the best fit for each scene

                You must output a JSON object in the following format:

                {{
                "media_type": "video",
                "caption": "str - used to post along with the video on social media",
                "comments": ["str", "str", "4 to 6 comments to post along with the video on social media to set the tone for engagement"],
                "background_music_url": "string or null - must come from available assets",
                "video_cover_url": "string or null - must come from available assets",
                "watermark": "str | dict - you can return the business logo url as string if available, or you can return a dictionary in the format: {{"text":"business name well-formatted", "text_color":"red | yellow | white | grey | etc", "font":"return a font name from the list below"}}",
                "scenes": [
                    {{
                    "media_type": "image | video",
                    "url": "string (must come from available assets)",
                    "overlay_text": "dict - should be in the format: {{"text":"text to be overlayed", "text_color":"green | red | black | white | etc", "font":"str - font name from the list of custom font names", "font_size": int - must be 60 or more}}",
                    "voice_over": "string (spoken narration text) that will be converted to audio via TTS",
                    "duration": number (seconds),
                    "transition": "fade | slide | null",
                    "fade_in": number (seconds),
                    "fade_out": number (seconds),
                    "animation": "zoom_in | pan | null",
                    "background_url": "string or null - image from assets"
                    }},
                    ...
                ]
                }}

                Rules:
                - Use only URLs from the available assets list.
                - Overlay text must be short, bold, and readable on mobile.
                - return font names only from the available custom font names list below:
                
                ### FONT NAMES ###
                - {', '.join(self.get_font().keys())}

                - Voice over should sound natural and persuasive.
                - Do not leave fields blank.
                - Do not add extra keys.
                - Output only valid JSON.
                - DO NOT REPEAT VIDEO PLAN. BE CREATIVE AND COMBINE ASSETS IN DIFFERENT PATTERNS TO CREATE UNIQUE VIDEO CONTENT THAT IS DIFFERENT FROM PREVIOUS CONTENTS

                ### PREVIOUS CONTENTS ###
                {"***".join(client.video_plan_history) if client.video_plan_history else ''}

        """.strip()
        # print(f"Prompt:\n{prompt}")
        video_plan = get_structured_data_from_gemini_smart(prompt)
        # print(f"Video plan: {video_plan}")
        # return
        if not video_plan:
            raise ValueError("Failed to generate video plan from AI")
        client.saved_video_plan = video_plan
        client.save(update_fields=["saved_video_plan"])
        return video_plan

    def get_font(self, name:str="") -> str | dict:
        font_map = {
            "impact": "fonts/impact.ttf",
            "impact-bold": "fonts/Impacted.ttf",
            "impact-unicode": "fonts/unicode.impact.ttf",
            "montserrat-b": "fonts/Montserrat-Black.ttf",
            "montserrat-bi": "fonts/Montserrat-BlackItalic.ttf",
            "montserrat-r": "fonts/Montserrat-Regular.ttf",
            "montserrat-ri": "fonts/Montserrat-Italic.ttf",
            "montserrat-l": "fonts/Montserrat-Light.ttf",
            "montserrat-li": "fonts/Montserrat-LightItalic.ttf",
            "bebas_b": "fonts/BebasNeue Bold.otf",
            "bebas_r": "fonts/BebasNeue Book.otf",
            "bebas_l": "fonts/BebasNeue Light.otf",
            "anton": "fonts/anton.ttf",
            "oswald-stencil": "fonts/Oswald-Stencil.ttf",
            "oswald-b": "fonts/Oswald-Bold.ttf",
            "oswald-r": "fonts/Oswald-Regular.ttf",
            "oswald-l": "fonts/Oswald-Light.ttf",
            "oswald-bi": "fonts/Oswald-BoldItalic.ttf",
            "oswald-ri": "fonts/Oswald-RegularItalic.ttf",
            "oswald-li": "fonts/Oswald-LightItalic.ttf"
        }
        if not name:
            return font_map
        return font_map.get(name, None)
    
    def wrap_text(self, text:str, font_size:int):
        tw = (WIDTH * 0.8) / (font_size * 0.6)
        lines = textwrap.wrap(text, width=int(tw))
        return "\\\n".join(lines) # Double backslash for FFmpeg parsing
    
    def make_scene(self, scene:dict, output_path:str):
        """
        Renders ONE scene to disk using FFmpeg (streaming, low memory)
        """
        duration = scene["duration"]
        width, height = WIDTH, HEIGHT

        # 1️⃣ Download media
        media_type = scene["media_type"]
        media_path = download(scene["url"], media_type=media_type)

        if scene.get("voice_over"):
            voice_path, _ = try_call_tts(scene["voice_over"])
            duration = get_media_duration(voice_path, "a")


        inputs = []
        filters = []
        audio_filters = []

        input_index = 0  # IMPORTANT: track -i inputs ONLY

        # 2️⃣ Base media input
        if media_type == "image":
            inputs += [
                "-loop", "1",
                "-t", str(duration),
                "-i", media_path
            ]
            input_index += 1
        else:
            self.make_scene_from_video(scene, output_path)
            return
            # inputs += ["-i", media_path]
            # input_index += 1

        # 3️⃣ Scale & crop to vertical
        filters.append(
            f"[0:v]setsar=1," # <--- CRITICAL: Resets pixel stretching first
            f"scale=w={width}:h={height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height}[v0]"
        )
        video_label = "v0"

        # 4️⃣ Zoom animation
        if scene.get("animation") == "zoom_in":
            filters.append(
                f"[{video_label}]"
                f"zoompan=z='min(zoom+0.0015,1.3)':d=1:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'[v1]"
            )
            video_label = "v1"

        # 5️⃣ Text overlay (watermark consistency fixed)
        overlay = scene.get("overlay_text", {})
        text = overlay.get("text")

        if text:
            text = self.format_text(text)
            font = self.get_font("montserrat-b")
            font_size = overlay.get("font_size", 60)
            color = overlay.get("text_color", "white")

            # filters.append(
            #     f"[{video_label}]drawtext="
            #     f"fontfile='{font}':"
            #     f"text='{text}':"
            #     f"fontsize={font_size}:"
            #     f"fontcolor={color}:"
            #     f"x=(w-text_w)/2:"
            #     f"y=h*0.78[text]"
            # )
            filters.append(
                f"[{video_label}]drawtext="
                f"fontfile='{font}':"
                f"text='{text}':"
                f"fontsize=64:"
                f"fontcolor=black:"
                f"box=1:"
                f"boxcolor=yellow:"
                f"boxborderw=15:"
                f"x=(w-text_w)/2:"
                f"y=h*0.75[text]"
            )
            video_label = "text"

        # 6️⃣ Fade effects (fade-out guaranteed to finish)
        if scene.get("fade_in"):
            filters.append(
                f"[{video_label}]"
                f"fade=t=in:st=0:d={scene['fade_in']}[fadin]"
            )
            video_label = "fadin"
        # Hard stop video timeline
        filters.insert(
            0,
            f"[{video_label}]trim=duration={duration},setpts=PTS-STARTPTS[vtrim]"
        )
        video_label = "vtrim"

        if scene.get("fade_out"):
            fade_out_dur = scene["fade_out"]
            fade_start = max(0, duration - fade_out_dur)

            filters.append(
                f"[{video_label}]"
                f"fade=t=out:st={fade_start}:d={fade_out_dur}[fadout]"
            )
            video_label = "fadout"
        
        # 7️⃣ Prepare Audio Inputs
        audio_inputs = []
        voice_path = None
        if scene.get("voice_over"):
            voice_path, _ = try_call_tts(scene["voice_over"])

        # We need a primary audio source to mix or use alone
        if voice_path:
            inputs += ["-i", voice_path]
            # Filter the voice-over immediately to ensure it's stereo 44.1k/48k for mixing
            # [v_a] ensures we have a standard format before the amix
            audio_filters.append(f"[{input_index}:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[vo_ready]")
            audio_inputs.append("[vo_ready]")
            input_index += 1

        # Add silent background so the video always has an audio track
        inputs += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
        audio_filters.append(f"[{input_index}:a]asetpts=PTS-STARTPTS[silence_ready]")
        audio_inputs.append("[silence_ready]")
        input_index += 1

        # 8️⃣ Mix Audio with Volume Normalization
        if len(audio_inputs) > 1:
            # mix the inputs, and use volume=2 to counter amix's 1/n scaling
            mix_str = "".join(audio_inputs)
            audio_filters.append(
                f"{mix_str}amix=inputs={len(audio_inputs)}:duration=first:dropout_transition=0,volume=2,"
                f"aresample=async=1000:min_hard_comp=0.100000[aout]"
                )
        else:
            audio_filters.append(f"{audio_inputs[0]}anull[aout]")

        full_filter_str = ";".join(filters) + ";" + ";".join(audio_filters)

        # 9️⃣ Final Command (Single Pass)
        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", full_filter_str,
            "-map", f"[{video_label}]",
            "-map", "[aout]",
            "-t", str(duration),
            "-c:v", "libx264",
            "-r", "30",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",      # Ensure decent audio bitrate
            "-ac", "2",          # Force output to 2 channels (stereo)
            "-movflags", "+faststart",
            output_path
        ]
        run(cmd)
    
    def make_scene_from_video(self, scene:dict, output_path:str):
        my_output_path = output_path.replace(".mp4", "_my_own.mp4")
        # width, height = WIDTH, HEIGHT

        # 1️⃣ Download media
        media_type = scene["media_type"]
        media_path = download(scene["url"], media_type=media_type)
        overlay = scene.get("overlay_text", {})
        text = overlay.get("text", "")
        font_size = 64
        text = self.wrap_text(text, font_size)
        font = self.get_font("montserrat-b")
        
        audio_path, _ = try_call_tts(scene["voice_over"])

        audio_duration = get_media_duration(audio_path, 'a')
        output_duration = audio_duration

        audio_filters = []
        apply_audio_filter = False
        video_filters = [
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease",
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2"
            # f"drawtext=fontfile={font}:text='{text}':fontsize={font_size}:fontcolor=black:box=1:boxcolor=yellow:boxborderw=15:line_spacing=10:x=(w-text_w)/2:y=h*0.75"
        ]

        # if scene.get("animation") == "zoom_in":
        #     # Example: simple zoom-in
        #     zoompan_filter = (
        #         f"zoompan=z='min(zoom+0.0005,1.05)':d=1:"
        #         f"x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
        #         # f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        #     )
        #     video_filters.append(zoompan_filter)  # apply before drawtext
        
        video_filters.append(f"drawtext=fontfile={font}:text='{text}':fontsize={font_size}:fontcolor=black:box=1:boxcolor=yellow:boxborderw=15:line_spacing=10:x=(w-text_w)/2:y=h*0.75")

        if scene.get("fade_in"):
            video_filters.append(f"fade=t=in:st=0:d={scene.get('fade_in')}")
            if apply_audio_filter:
                audio_filters.append(f"afade=t=in:st=0:d={scene.get('fade_in')}")
        if scene.get("fade_out"):
            video_filters.append(f"fade=t=out:st={output_duration-scene.get('fade_out')}:d={scene.get('fade_out')}")
            if apply_audio_filter:
                audio_filters.append(f"afade=t=out:st={audio_duration-scene.get('fade_out')}:d={scene.get('fade_out')}")
        
        audio_filter_str = ",".join(audio_filters) if audio_filters else None
        video_filter_str = ",".join(video_filters)
        
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", media_path,
            "-i", audio_path,
            "-filter_complex",
            f"[1:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,asetpts=PTS-STARTPTS[aout]",
            "-map", "0:v:0",
            "-map", "[aout]",
            "-vf", video_filter_str,
            "-r", "30",           # Force 30 FPS for THIS clip
            "-c:v", "libx264",
            "-c:a", "aac",
            "-ac", "2",
            "-ar", "44100",
            "-b:a", "192k",
            "-shortest",
            "-preset", "ultrafast",
            "-crf", "20",
            my_output_path
        ]
        run(cmd)

        # cut video to audio length
        self.cut_video(my_output_path, output_duration, output_path)

    def make_cover(self, cover_url, output_path):
        """
        Renders a 1.2s vertical cover video with a silent audio track 
        to ensure compatibility with voice-over scenes during concat.
        """
        duration = 1.2
        image_path = download(cover_url, media_type="image")

        # Scale and crop logic
        filter_chain = f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},setsar=1"

        cmd = [
            "ffmpeg", "-y",
            # Input 0: The Image
            "-loop", "1",
            "-t", str(duration),
            "-i", image_path,
            # Input 1: Virtual silence generator (crucial for concat)
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-vf", filter_chain,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            # Audio encoding settings
            "-c:a", "aac",
            "-ac", "2",           # 2 channels (stereo)
            "-ar", "44100",       # 44.1kHz sample rate
            "-map", "0:v",        # Map video from image
            "-map", "1:a",        # Map audio from silence generator
            "-shortest",          # Match duration to the video
            "-movflags", "+faststart",
            output_path
        ]

        subprocess.run(cmd, check=True)
        
    def make_watermark(self, watermark, duration, video_width=WIDTH, video_height=HEIGHT):
        """
        Returns FFmpeg inputs and overlay filter for watermark
        Supports:
        - image watermark (URL)
        - text watermark (dict)
        """

        inputs = []
        filter_part = ""

        # 🖼 IMAGE WATERMARK
        if isinstance(watermark, str):
            # logo_path = download(watermark, media_type="image")
            logo_path = self.get_cached_logo(watermark)

            # ✅ Ensure WEBP (CPU + consistency fix)
            logo_path = self.ensure_webp(logo_path)
            if Path(logo_path).exists():
                inputs = [
                    "-loop", "1",
                    "-t", str(duration),
                    "-i", logo_path
                ]

                # # ✅ Scale relative to video, consistent opacity
                # wm_width = int(video_width * 0.12)

                # filter_part = (
                #     f"[1:v]scale={wm_width}:-1,format=rgba,"
                #     f"colorchannelmixer=aa=0.6[wm];"
                #     f"[0:v][wm]overlay="
                #     f"x={video_width}-overlay_w-20:"
                #     f"y=20"
                # )
                static_size = 150 

                filter_part = (
                    # 1. Scale to square, force original aspect ratio to fit inside without stretching
                    # 2. format=rgba ensures transparency is preserved
                    # 3. colorchannelmixer sets opacity to 60%
                    f"[1:v]scale={static_size}:{static_size}:force_original_aspect_ratio=decrease,"
                    # f"crop={static_size}:{static_size},format=rgba,"
                    f"pad={static_size}:{static_size}:(ow-iw)/2:(oh-ih)/2:color=white,"
                    f"format=rgba," 
                    f"colorchannelmixer=aa=0.6[wm];"
                    # 4. Overlay at the top right with 20px padding
                    f"[0:v][wm]overlay="
                    f"x={video_width}-overlay_w-20:"
                    f"y=20"
                )

        # 📝 TEXT WATERMARK
        else:
            text = self.format_text(watermark.get("text", ""))
            # text = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")

            font = self.get_font(watermark.get("font", "anton"))
            color = watermark.get("text_color", "white")
            size = watermark.get("font_size", 42)

            filter_part = (
                f"[0:v]drawtext="
                f"fontfile='{font}':"
                f"text='{text}':"
                f"fontsize={size}:"
                f"fontcolor={color}:"
                f"x={video_width}-text_w-20:"
                f"y=20"
            )

        return inputs, filter_part

    def test_with_a_scene(self):
        """This is used to test all parts of the code to generate one scene only"""
        output = f"temp_media/{uuid.uuid4()}_final.mp4"
        plan = self.video_plan["scenes"][0]

        # create scene 
        scene = self.make_scene(plan)

        # add watermark if specified
        if self.video_plan.get("watermark"):
            watermark = self.make_watermark(self.video_plan["watermark"], duration=scene.duration)
            scene = CompositeVideoClip([scene, watermark], size=scene.size)

        # Background music
        music = None
        if self.video_plan.get("background_music_url"):
            music_path = download(self.video_plan["background_music_url"], media_type="audio")
            music = AudioFileClip(music_path)

            music = music.with_effects([MultiplyVolume(0.2)])
            music = music.subclipped(0, scene.duration)

            if scene.audio:
                final_audio = CompositeAudioClip([scene.audio, music])
            else:
                final_audio = music

            scene = scene.with_audio(final_audio)
        
        cover_clip = None
        # add cover image at start
        if len(self.video_plan["scenes"]) > 2:
            cover_clip = self.make_cover(self.video_plan.get("video_cover_url", self.video_plan["scenes"][2]["url"]))
            scene = concatenate_videoclips([cover_clip, scene], method="compose")


        # Render
        scene.write_videofile(
            output, 
            fps=24, 
            codec="libx264",
            preset="ultrafast",
            threads=4, 
            audio_codec="aac")

        # Cleanup ffmpeg resources
        if scene.audio:
            scene.audio.close()

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

        scene.close()
        cover_clip.close()
        # Delete temp assets
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))
        

        # Save video path in video plan
        # client = AutomatedClients.objects.get(client_id=self.page_id)
        # video_plan = client.saved_video_plan
        # video_plan["final_video_path"] = output

        # client.saved_video_plan = video_plan
        # client.save(update_fields=["saved_video_plan"])
        return output, "success"
    
    def ensure_webp(self, image_path: str) -> str:
        """
        Converts image to WEBP if needed and returns the WEBP path.
        If already WEBP, returns original path.
        """
        src = Path(image_path)

        if src.suffix.lower() == ".webp":
            return str(src)

        webp_path = src.with_suffix(".webp")

        subprocess.run([
            "ffmpeg", "-y",
            "-i", str(src),
            "-pix_fmt", "yuv420p",
            str(webp_path)
        ], check=True)

        return str(webp_path)

    def get_cached_logo(self, logo_url: str) -> str:
        # 1️⃣ Stable cache key (same URL → same key)
        key = "logo:" + hashlib.sha1(logo_url.encode()).hexdigest()

        # 2️⃣ Redis lookup
        cached_path = get_cache(key)
        if cached_path and Path(cached_path).exists():
            return cached_path

        # 3️⃣ Download once
        logo_path = download(logo_url, media_type="image")

        # 4️⃣ Convert once
        logo_path = self.ensure_webp(logo_path)

        # 5️⃣ Move to permanent cache location
        final_path = LOGO_CACHE_DIR / Path(logo_path).name
        Path(logo_path).replace(final_path)

        # 6️⃣ Store path in Redis
        save_cache(key, str(final_path), None)

        return str(final_path)
    
    def format_text(self, text: str):
        """
        Escapes characters for FFmpeg drawtext filter.
        Note: Single quotes in FFmpeg filter_complex are extremely sensitive.
        """
        # 1. Handle backslashes first
        text = text.replace("\\", "\\\\")
        # 2. Handle colons (separator for filter options)
        text = text.replace(":", "\\:")
        # 3. Handle single quotes: FFmpeg requires '...' to contain them, 
        # but the quote itself must be escaped as \' and the backslash must be escaped.
        # Effectively, for many FFmpeg versions, replacing ' with ’ (smart quote) 
        # or removing it is safer, but here is the correct escape:
        text = text.replace("'", "'\\''") 
        
        return text
    
    def cut_video(self, video_path, duration, output_path=None):
        """
        Cuts a video to the given duration without re-encoding.
        
        Parameters:
            video_path (str): Path to the input video.
            duration (float or int): Duration in seconds to cut.
            output_path (str, optional): Path for the output video. 
                If None, a new file will be created in the same directory with '_cut' suffix.
        
        Returns:
            str: Path to the trimmed video file.
        """
        if output_path is None:
            base, ext = os.path.splitext(video_path)
            output_path = f"{base}_cut{ext}"
        
        cmd = [
            "ffmpeg",
            "-y",                   # overwrite output if exists
            "-i", video_path,       # input video
            "-t", str(duration),    # duration to keep
            "-c", "copy",           # stream copy (no re-encoding)
            output_path
        ]
        
        subprocess.run(cmd, check=True)
        return output_path
    
    def render(self):
        # output = f"temp_media/{uuid.uuid4()}_final.mp4"
        TEMP_DIR = "temp_media"
        total_duration = [0]

        job_id = uuid.uuid4().hex
        workdir = Path(TEMP_DIR) / job_id
        workdir.mkdir(parents=True, exist_ok=True)

        scene_files = []
        message = ""
        final_output = f"{TEMP_DIR}/{job_id}_final.mp4"

        try:
            # 1️⃣ Render scenes individually
            for i, scene in enumerate(self.video_plan["scenes"], start=1):
                out = workdir / f"scene_{i}.mp4"
                self.make_scene(scene, str(out))  # MUST render via ffmpeg
                # if i != 2:
                #     scene_files.append(out)
                scene_files.append(out)
                print(f"{out} created")
                try:
                    total_duration.append(float(scene.get("duration")))
                except Exception as e:
                    print(f"Error adding duration: \n{e}")
                    total_duration.append(0)

            # 2️⃣ Render cover
            cover = workdir / "cover.mp4"
            self.make_cover(
                self.video_plan.get("video_cover_url", self.video_plan["scenes"][0]["url"]),
                str(cover)
            )

            # Insert cover at start
            scene_files.insert(0, cover)

            # 3️⃣ Create concat file
            concat_file = workdir / "concat.txt"
            with open(concat_file, "w") as f:
                for file in scene_files:
                    f.write(f"file '{file.resolve()}'\n")

            base_video = workdir / "base.mp4"
            run([
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",
                "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
                str(base_video)
            ])
            # run([
            #     "ffmpeg", "-y",
            #     "-f", "concat", "-safe", "0",
            #     "-i", str(concat_file),
            #     "-c:v", "copy",                 # copy video only
            #     "-c:a", "aac",                  # re-encode audio
            #     "-ar", "44100",
            #     "-ac", "2",
            #     "-b:a", "192k",
            #     str(base_video)
            # ])

            current_video = base_video

            # # 4️⃣ Watermark (optional)
            video_duration = get_video_duration(current_video)
            if self.video_plan.get("watermark"):
                wm_inputs, wm_filter = self.make_watermark(
                    self.video_plan["watermark"],
                    duration=video_duration
                )

                watermarked = workdir / "watermarked.mp4"

                cmd = [
                    "ffmpeg", "-y",
                    "-threads", "2",
                    "-i", str(current_video),
                    *wm_inputs,
                    "-filter_complex", wm_filter,
                    "-map", "0:v",
                    "-map", "0:a?",
                    "-c:a", "copy",
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p",
                    str(watermarked)
                ]

                subprocess.run(cmd, check=True)
                current_video = watermarked

            # 5️⃣ Background music (optional)
            if self.video_plan.get("background_music_url"):
                music_path = download(self.video_plan["background_music_url"], media_type="audio")
                music_video = workdir / "with_music.mp4"
                if has_audio(current_video):
                    run([
                        "ffmpeg", "-y",
                        "-i", str(current_video),
                        "-i", music_path,
                        "-filter_complex",
                        "[1:a]volume=0.2[a1];[0:a][a1]amix=inputs=2:duration=shortest",
                        "-c:v", "copy",
                        str(music_video)
                    ])
                else:
                    run([
                        "ffmpeg", "-y",
                        "-i", str(current_video),
                        "-i", music_path,
                        "-c:v", "copy",
                        "-map", "0:v",
                        "-map", "1:a",
                        "-shortest",
                        str(music_video)
                    ])

                current_video = music_video
            v_duration = get_audio_duration_from_video(current_video)
            self.cut_video(current_video, v_duration, final_output)

            # 6️⃣ Finalize
            # shutil.move(current_video, final_output)

            # 7️⃣ Save result
            client = AutomatedClients.objects.get(client_id=self.page_id)
            self.save_video_plan_to_history(client)

            video_plan = client.saved_video_plan
            video_plan["final_video_path"] = final_output
            client.saved_video_plan = video_plan
            client.save(update_fields=["saved_video_plan"])

            message = "Video rendered successfully"
        except Exception as e:
            message = f"Render failed: {e}"
            print(message)
            final_output = None

        finally:
          
            # 🧹 HARD CLEANUP
            for item in workdir.glob("*"):
                try:
                    item.unlink()
                except:
                    pass
            asset_dir = Path("temp_assets")
            for item in  asset_dir.glob("*"):
                try:
                    item.unlink()
                except:
                    pass
            workdir.rmdir()

        return final_output, message
    
    def save_video_plan_to_history(self, client: AutomatedClients, max_entry:int=10):
        entries = client.video_plan_history
        if entries:  #  and len(entries) >= max_entry:
            last_nine = entries[-(max_entry - 1):]
            last_nine.append(client.saved_video_plan)
            client.video_plan_history = last_nine
            client.save(update_fields=['video_plan_history'])
        else:
            client.video_plan_history = [client.saved_video_plan]
            client.save(update_fields=['video_plan_history'])