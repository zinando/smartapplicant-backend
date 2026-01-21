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

WIDTH = 1080
HEIGHT = 1920

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
    
    def make_scenexxx(self, scene):
        global is_base_open, is_voice_open, base, voice

        try:
            # Download media
            if scene["media_type"] == "video":
                media_path = download(scene["url"], media_type="video")
                base = VideoFileClip(media_path).with_duration(scene["duration"])
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
                text=scene["overlay_text"].get("text", ""),
                font_size=scene["overlay_text"].get("font_size", 60),
                color=scene["overlay_text"].get("text_color", "white"),
                font= self.get_font(scene["overlay_text"].get("font", "montserrat-r")),
                size=(900, 450),
                method="caption"
            ).with_duration(scene["duration"]).with_position(("center", 0.78), relative=True)

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
            # final = base

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
        
    def make_scene(self, scene:dict, output_path:str):
        """
        Renders ONE scene to disk using FFmpeg (streaming, low memory)
        """
        # temp_out_put = output_path.replace(".mp4", "_silent.mp4")
        # vo_output = output_path.replace(".mp4", "_vo_vid.mp4")

        duration = scene["duration"]
        width, height = WIDTH, HEIGHT

        # 1️⃣ Download media
        media_type = scene["media_type"]
        media_path = download(scene["url"], media_type=media_type)

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
            inputs += ["-i", media_path]
            input_index += 1

        # 3️⃣ Scale & crop to vertical
        filters.append(
            f"[0:v]"
            f"scale=w={width}:h={height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},setsar=1[v0]"
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
            font = self.get_font(overlay.get("font", "montserrat-r"))
            font_size = overlay.get("font_size", 60)
            color = overlay.get("text_color", "white")

            filters.append(
                f"[{video_label}]drawtext="
                f"fontfile='{font}':"
                f"text='{text}':"
                f"fontsize={font_size}:"
                f"fontcolor={color}:"
                f"x=(w-text_w)/2:"
                f"y=h*0.78[text]"
            )
            video_label = "text"

        # 6️⃣ Fade effects (fade-out guaranteed to finish)
        if scene.get("fade_in"):
            filters.append(
                f"[{video_label}]"
                f"fade=t=in:st=0:d={scene['fade_in']}[fadin]"
            )
            video_label = "fadin"

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
            audio_filters.append(f"{mix_str}amix=inputs={len(audio_inputs)}:duration=first:dropout_transition=0,volume=2[aout]")
        else:
            audio_filters.append(f"{audio_inputs[0]}copy[aout]")

        full_filter_str = "; ".join(filters) + "; " + "; ".join(audio_filters)

        # 9️⃣ Final Command (Single Pass)
        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", full_filter_str,
            "-map", f"[{video_label}]",
            "-map", "[aout]",
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",      # Ensure decent audio bitrate
            "-ac", "2",          # Force output to 2 channels (stereo)
            "-movflags", "+faststart",
            output_path
        ]
        run(cmd)

        # # 7️⃣ Audio inputs
        # audio_inputs = []
        # voice_path = None

        # # Optional voice-over
        # if scene.get("voice_over"):
        #     voice_path, _ = try_call_tts(scene["voice_over"])
        # if voice_path:
        #     inputs += ["-i", voice_path]
        #     audio_inputs.append(f"[{input_index}:a]")
        #     input_index += 1
        # else:
        #     print("⚠️ Voice-over failed, using silence")

        #     # Always add silence fallback
        #     inputs += [
        #         "-f", "lavfi",
        #         "-i", "anullsrc=channel_layout=mono:sample_rate=24000"
        #     ]
        #     audio_inputs.append(f"[{input_index}:a]")
        #     input_index += 1

        # # 8️⃣ Audio filter graph
        # if len(audio_inputs) == 1:
        #     audio_filters.append(
        #         f"{audio_inputs[0]}asetpts=PTS-STARTPTS[aout]"
        #     )
        # else:
        #     audio_filters.append(
        #         f"{''.join(audio_inputs)}"
        #         f"amix=inputs={len(audio_inputs)}:duration=first[aout]"
        #     )

        # # 9️⃣ Assemble FFmpeg command
        # cmd = [
        #     "ffmpeg", "-y",
        #     *inputs,
        #     "-filter_complex", ";".join(filters + audio_filters),
        #     # "-filter_complex", ";".join(filters),
        #     "-map", f"[{video_label}]",
        #     "-map", "[aout]",
        #     "-t", str(duration),
        #     "-c:v", "libx264",
        #     "-preset", "ultrafast",
        #     "-pix_fmt", "yuv420p",
        #     "-c:a", "aac",
        #     "-movflags", "+faststart",
        #     output_path
        # ]
        # run(cmd)

        # # current_video = temp_out_put

        # # # add voice over here
        # # if scene.get("voice_over"):
        # #     voice_path, _ = try_call_tts(scene["voice_over"])
        # #     if voice_path:
        # #         run([
        # #             "ffmpeg", "-y",
        # #             "-i", str(current_video),
        # #             "-i", voice_path,
        # #             "-c:v", "copy",
        # #             "-c:a", "aac",
        # #             "-map", "0:v:0",
        # #             "-map", "1:a:0",
        # #             "-shortest",
        # #             str(vo_output)
        # #         ])
        # #         current_video = vo_output

        # #     else:
        # #         print("⚠️ Voice-over failed, using silence")
        
        # os.rename(current_video, output_path)

    def make_sceneyyy(self, scene, output_path):
        """
        Renders ONE scene to disk using FFmpeg (streaming, low memory)
        """

        duration = scene["duration"]
        width, height = WIDTH, HEIGHT

        # 1️⃣ Download media
        media_type = scene["media_type"]
        media_path = download(scene["url"], media_type=media_type)

        inputs = []
        filters = []
        input_index = 0

        # 2️⃣ Base media input
        if media_type == "image":
            inputs += ["-loop", "1", "-t", str(duration), "-i", media_path]
        else:
            inputs += ["-i", media_path]

        # 3️⃣ Scale & crop to vertical
        filters.append(
            f"[0:v]scale=w={width}:h={height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},setsar=1[v0]"
        )

        video_label = "v0"

        # 4️⃣ Zoom animation
        if scene.get("animation") == "zoom_in":
            filters.append(
                f"[{video_label}]zoompan=z='min(zoom+0.0015,1.3)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'[v1]"
            )
            video_label = "v1"

        # 5️⃣ Text overlay
        text = scene.get("overlay_text", {}).get("text")
        if text:
            font = self.get_font(scene["overlay_text"].get("font", "montserrat-r"))
            font_size = scene["overlay_text"].get("font_size", 60)
            color = scene["overlay_text"].get("text_color", "white")

            filters.append(
                f"[{video_label}]drawtext="
                f"fontfile='{font}':"
                f"text='{text}':"
                f"fontsize={font_size}:"
                f"fontcolor={color}:"
                f"x=(w-text_w)/2:"
                f"y=h*0.78[text]"
            )
            video_label = "text"

        # 6️⃣ Fade effects
        if scene.get("fade_in"):
            filters.append(
                f"[{video_label}]fade=t=in:st=0:d={scene['fade_in']}[fadin]"
            )
            video_label = "fadin"

        if scene.get("fade_out"):
            filters.append(
                f"[{video_label}]fade=t=out:st={duration-scene['fade_out']}:d={scene['fade_out']}[fadout]"
            )
            video_label = "fadout"

        # 7️⃣ Voice-over (optional)
        audio_inputs = []
        audio_filters = []

        # Track how many inputs already exist
        input_index = len(inputs) // 2

        # Optional voice-over
        if scene.get("voice_over"):
            voice_path, _ = try_call_tts(scene["voice_over"])
            if voice_path:
                inputs += ["-i", voice_path]
                audio_inputs.append(f"[{input_index}:a]")
                input_index += 1
            else:
                print("⚠️ Voice-over failed, falling back to silence")

        # Always add silence (fallback)
        inputs += [
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=mono:sample_rate=24000"
        ]
        audio_inputs.append(f"[{input_index}:a]")

        # Build audio filter graph
        if len(audio_inputs) == 1:
            audio_filters.append(
                f"{audio_inputs[0]}asetpts=PTS-STARTPTS[aout]"
            )
        else:
            audio_filters.append(
                f"{''.join(audio_inputs)}amix=inputs={len(audio_inputs)}:duration=shortest[aout]"
            )
        
        # 8️⃣ Assemble FFmpeg command
        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", ";".join(filters + audio_filters),
            "-map", f"[{video_label}]",
            "-map", "[aout]",
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-movflags", "+faststart",
            output_path
        ]
        
        subprocess.run(cmd, check=True)
    
    def make_coverxxx(self, cover_url):
        # ownload the cover image
        cover = download(cover_url, media_type="image")
        cover_obj = ImageClip(cover).with_duration(1.2)
        cover_obj = cover_obj.with_effects([vfx.Resize(height=HEIGHT)])
        if cover_obj.w < WIDTH:
            cover_obj = cover_obj.with_effects([vfx.Resize(width=WIDTH)])
        return cover_obj
    
    def make_coveryyy(self, cover_url, output_path):
        """
        Renders a 1.2s vertical cover video from an image using FFmpeg
        """

        duration = 1.2
        image_path = download(cover_url, media_type="image")

        # Scale to HEIGHT first, then pad/crop to WIDTH x HEIGHT
        filter_chain = f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT}"
        # (
        #     # f"scale=-2:{HEIGHT}:force_original_aspect_ratio=decrease,"
        #     f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT}"
        #     # f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2"
        # )
        # "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-t", str(duration),
            "-i", image_path,
            "-vf", filter_chain,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            output_path
        ]

        subprocess.run(cmd, check=True)
    
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
    
    def make_watermarkxxx(self, input:str|dict, duration:float=10):
        """Creates a watermark clip from text or logo image"""
        # if input.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) or any(s in input for s in ["https://", "http://", "www.", "drive.google.com"]):
        if isinstance(input, str):    
            # Treat as image URL
            logo_path = download(input, media_type="image")
            watermark = (ImageClip(logo_path)
                         .with_duration(duration)
                         .with_effects([vfx.Resize(height=100)])
                         .with_position((920, 20))
                        #  .with_margin(right=10, top=10)
                         .with_opacity(0.7))
        else:
            # Treat as text :1080, 1920
            # if you dont set bgcolor and transparency, dont set opacity
            watermark = (TextClip(
                text=input.get("text", ""), 
                font_size=42,
                font=self.get_font(input.get("font", "anton")),
                size=(None, 60), 
                color= input.get("text_color", "white") 
                )
                         .with_duration(duration)
                         .with_position((900, 20))
                        )
        return watermark
    
    def make_watermarkyyy(self, watermark, duration, video_width=WIDTH, video_height=HEIGHT):
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
            logo_path = download(watermark, media_type="image")
            
            # convert logo image to webp
            logo_path = self.ensure_webp(logo_path)

            inputs = [
                "-loop", "1",
                "-t", str(duration),
                "-i", logo_path
            ]

            filter_part = (
                "[1:v]scale=-1:100,format=rgba,colorchannelmixer=aa=0.7[wm];"
                "[0:v][wm]overlay=920:20"
            )

        # 📝 TEXT WATERMARK
        else:
            text = watermark.get("text", "")
            text = text.replace(":", "\\:").replace("'", "\\'")
            font = self.get_font(watermark.get("font", "anton"))
            color = watermark.get("text_color", "white")

            filter_part = (
                f"[0:v]drawtext="
                f"fontfile='{font}':"
                f"text='{text}':"
                f"fontsize=42:"
                f"fontcolor={color}:"
                f"x=900:y=20"
            )

        return inputs, filter_part
    
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

            inputs = [
                "-loop", "1",
                "-t", str(duration),
                "-i", logo_path
            ]

            # ✅ Scale relative to video, consistent opacity
            wm_width = int(video_width * 0.12)

            filter_part = (
                f"[1:v]scale={wm_width}:-1,format=rgba,"
                f"colorchannelmixer=aa=0.6[wm];"
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
    
    def renderxxx(self):
        output = f"temp_media/{uuid.uuid4()}_final.mp4"
        global is_base_open, is_voice_open, base, voice
        open_audio_clips = []
        message = ""

        try:
            # Build scenes
            for scene in self.video_plan["scenes"]:
                clip = self.make_scene(scene)
                self.clips.append(clip)
                print(f"Generated scene {self.video_plan['scenes'].index(scene) + 1} with URL: {scene.get('url')}")

            # add cover image at start
            cover_clip = self.make_cover(self.video_plan.get("video_cover_url", self.video_plan["scenes"][0]["url"]))
            self.clips.insert(0, cover_clip)

            video = concatenate_videoclips(self.clips, method="compose")

            # add watermark if specified
            if self.video_plan.get("watermark"):
                watermark = self.make_watermark(self.video_plan["watermark"], duration=video.duration)
                video = CompositeVideoClip([video, watermark], size=video.size)

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
            video.write_videofile(output, fps=24, codec="libx264", preset="ultrafast", threads=4, audio_codec="aac")

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

            # Save video path in video plan
            client = AutomatedClients.objects.get(client_id=self.page_id)
            video_plan = client.saved_video_plan
            video_plan["final_video_path"] = output

            client.saved_video_plan = video_plan
            client.save(update_fields=["saved_video_plan"])
            
            message = "Video rendered successfully"
            print(message)
        except Exception as e:
            print(f"Error rendering video: {e}")
            output = None
            message = str(e)

        return output, message

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
    
    def format_text(self, text:str):
        """Removes or escapes special characters"""
        return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    
    def render(self):
        # output = f"temp_media/{uuid.uuid4()}_final.mp4"
        TEMP_DIR = "temp_media"

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
                scene_files.append(out)
                print(f"{out} created")

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
                str(base_video)
            ])

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

            # 6️⃣ Finalize
            shutil.move(current_video, final_output)

            # 7️⃣ Save result
            client = AutomatedClients.objects.get(client_id=self.page_id)
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