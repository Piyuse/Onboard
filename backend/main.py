import cv2
import numpy as np
import moviepy.editor as mp
import os
import time
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, jsonify
from llm_handler import generate_text, GEMINI_API_KEY

app = Flask(__name__)

# Paths
IMAGE_PATHS = ["static/images/birthday.jpg"]
OUTPUT_VIDEO = "output_ad.mp4"
FINAL_VIDEO = "final_ad.mp4"
FONT_PATH = "static/fonts/cur.ttf"

# Load font
try:
    font = ImageFont.truetype(FONT_PATH, 40)
except IOError:
    print("Warning: Font file not found. Using default font.")
    font = ImageFont.load_default()

def split_text(text, max_words=5):
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

def generate_video(text):
    frames = []
    text_segments = split_text(text, max_words=5)
    
    os.makedirs(os.path.dirname(IMAGE_PATHS[0]), exist_ok=True)
    
    for img_path in IMAGE_PATHS:
        if not os.path.exists(img_path):
            blank_img = Image.new('RGB', (640, 480), color=(0, 0, 120))
            draw = ImageDraw.Draw(blank_img)
            draw.text((50, 240), "Sample Image", fill="white")
            blank_img.save(img_path)
            print(f"Created sample image at {img_path}")
        
        try:
            image = Image.open(img_path)
            img_height = image.height
            
            for segment in text_segments:
                # Generate multiple frames for animation
                for step in range(20):  # Number of frames for animation
                    img_copy = image.copy()
                    draw = ImageDraw.Draw(img_copy)
                    
                    # Calculate text position moving upwards
                    start_y = img_height - 100  # Start near bottom
                    end_y = 100  # End near top
                    text_y = start_y - (start_y - end_y) * (step / 19)  # Linear interpolation
                    text_position = (100, int(text_y))
                    
                    # Draw semi-transparent background rectangle
                    text_width = len(segment) * 15
                    draw.rectangle(
                        [text_position[0] - 5, text_position[1] - 5, 
                         text_position[0] + text_width, text_position[1] + 35],
                        fill=(0, 0, 0, 128)
                    )
                    # Draw animated text
                    draw.text(text_position, segment, font=font, fill="white")
                    
                    # Convert to OpenCV format and add to frames
                    frame = cv2.cvtColor(np.array(img_copy), cv2.COLOR_RGB2BGR)
                    frames.append(frame)
                    
        except Exception as e:
            print(f"Error processing image {img_path}: {e}")
            return None

    if not frames:
        print("Error: No frames were generated.")
        return None
    
    try:
        height, width, _ = frames[0].shape
        video = cv2.VideoWriter(OUTPUT_VIDEO, cv2.VideoWriter_fourcc(*"mp4v"), 10, (width, height))  # Increased FPS to 10
        for frame in frames:
            video.write(frame)
        video.release()

        time.sleep(2)  # Ensure file is properly written
        clip = mp.VideoFileClip(OUTPUT_VIDEO)
        clip.write_videofile(FINAL_VIDEO, codec="libx264")
        clip.close()
        return FINAL_VIDEO
    except Exception as e:
        print(f"Error in video generation: {e}")
        return None

@app.route('/generate-ad', methods=['POST'])
def generate_ad():
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        ad_text = generate_text(prompt) 
        video_path = generate_video(ad_text)
        if not video_path:
            return jsonify({"error": "Failed to generate video."}), 500

        return jsonify({"advertisement": ad_text, "video": video_path, "status": "success"})
    except Exception as e:
        print(f"Exception in generate_ad endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "Server is running"})

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("WARNING: No Gemini API key found. Using fallback text generation.")
    os.makedirs("static/images", exist_ok=True)
    app.run(debug=True)