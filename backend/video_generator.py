import moviepy.editor as mp
from moviepy.video.tools.subtitles import SubtitlesClip
import os

IMAGES_PATH = "backend/static/images"
VIDEO_OUTPUT = "backend/static/videos"

def create_video(ad_text):
    images = sorted([os.path.join(IMAGES_PATH, img) for img in os.listdir(IMAGES_PATH)])
    clips = [mp.ImageClip(img, duration=2) for img in images]

    # Create text clip
    txt_clip = mp.TextClip(ad_text, fontsize=30, color='white', size=(640, 100)).set_duration(len(clips) * 2).set_position(('center', 'bottom'))

    # Concatenate images and overlay text
    video = mp.concatenate_videoclips(clips).set_fps(24).set_audio(None)
    final_video = mp.CompositeVideoClip([video, txt_clip])

    # Save video
    output_path = os.path.join(VIDEO_OUTPUT, "generated_ad.mp4")
    final_video.write_videofile(output_path, codec="libx264", fps=24)

    return output_path
