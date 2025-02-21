import cv2
import numpy as np
import moviepy.editor as mp
import os
import time
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, jsonify
from llm_handler import generate_text

app = Flask(__name__)

# Path to images that will be used in the video
IMAGE_PATHS = ["static/images/minions.jpg"]  # Ensure the path is correct

# Video output path
OUTPUT_VIDEO = "output_ad.mp4"
FINAL_VIDEO = "final_ad.mp4"

# Load font
try:
    font = ImageFont.truetype("arial.ttf", 30)
except IOError:
    print("Warning: Font file not found. Using default font.")
    font = ImageFont.load_default()

def generate_video(text):
    """Generate a video using predefined images and LLM-generated text."""
    frames = []

    for img_path in IMAGE_PATHS:
        # Check if image exists
        if not os.path.exists(img_path):
            print(f"Error: Image file '{img_path}' not found.")
            return None
        
        try:
            # Load image
            image = Image.open(img_path)
            draw = ImageDraw.Draw(image)
            
            # Add text overlay
            text_position = (100, 50)
            draw.text(text_position, text, font=font, fill="white")
            
            # Convert to OpenCV format
            frame = np.array(image)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frames.append(frame)
        except Exception as e:
            print(f"Error processing image {img_path}: {e}")
            return None

    # Check if frames were generated
    if not frames:
        print("Error: No frames were generated.")
        return None
    
    # Define video writer
    height, width, layers = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, 1, (width, height))
    
    for frame in frames:
        video.write(frame)
    
    video.release()
    cv2.destroyAllWindows()

    # Check if video was created
    if not os.path.exists(OUTPUT_VIDEO):
        print(f"Error: {OUTPUT_VIDEO} was not created.")
        return None
    
    print(f"Video saved as {OUTPUT_VIDEO}")
    
    # Convert to MP4 using MoviePy
    try:
        time.sleep(2)  # Small delay to ensure file is written
        clip = mp.VideoFileClip(OUTPUT_VIDEO)
        clip.write_videofile(FINAL_VIDEO, codec="libx264")
    except Exception as e:
        print(f"Error converting video: {e}")
        return None
    
    return FINAL_VIDEO

@app.route('/generate-ad', methods=['POST'])
def generate_ad():
    try:
        data = request.get_json()
        prompt = data.get("prompt")

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Generate advertisement text using LLM
        ad_text = generate_text(prompt)
        
        if not ad_text:
            return jsonify({"error": "Failed to generate text."}), 500

        # Generate video with text overlay
        video_path = generate_video(ad_text)
        
        if not video_path:
            return jsonify({"error": "Failed to generate video."}), 500

        return jsonify({"advertisement": ad_text, "video": video_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)