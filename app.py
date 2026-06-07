from dotenv import load_dotenv
import os
import re
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import requests

load_dotenv()

app = Flask(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def get_video_id(url):
    patterns = [
        r"v=([0-9A-Za-z_-]{11})",
        r"youtu\.be/([0-9A-Za-z_-]{11})",
        r"youtube\.com/shorts/([0-9A-Za-z_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_info(url):
    video_id = get_video_id(url)
    if not video_id:
        return None

    api_key = os.getenv("YOUTUBE_API_KEY")
    
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={
            "part": "snippet",
            "id": video_id,
            "key": api_key
        }
    )
    
    data = response.json()
    
    if not data.get("items"):
        return None
    
    item = data["items"][0]["snippet"]
    title = item.get("title", "")
    description = item.get("description", "")
    
    return f"Title: {title}\n\nDescription: {description}"

@app.route("/")
def home():
    return render_template("index2.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    url = request.json.get("url")

    if not url:
        return jsonify({"result": "No URL provided"})

    video_text = get_video_info(url)

    if not video_text:
        return jsonify({"result": "Could not fetch video. Make sure it is a valid public YouTube link!"})

    prompt = f"""
Based on this YouTube video information, give:

1. A clear summary (4 to 15 sentences)
2. 5 key bullet points
3. 5 quiz questions with answers

No markdown. No symbols. Plain text only.

Video info:
{video_text[:8000]}
"""

    try:
        response = model.generate_content(prompt)
        return jsonify({"result": response.text})
    except:
        return jsonify({"result": "AI quota exceeded. Try again in a few minutes!"})

if __name__ == "__main__":
    app.run(debug=True)