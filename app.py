import shutil

from dotenv import load_dotenv
import os
import re
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import yt_dlp

load_dotenv()

app = Flask(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def get_transcript(url):
    cookies_content = os.getenv("COOKIES_CONTENT")
    if cookies_content:
        with open("cookies.txt", "w") as f:
            f.write(cookies_content)
                    
    import shutil
if os.path.exists("/etc/secrets/cookies.txt"):
    shutil.copy("/etc/secrets/cookies.txt", "/tmp/cookies.txt")
    cookies_path = "/tmp/cookies.txt"
else:
    cookies_path = "cookies.txt"
    
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': True,
        'quiet': True,
        'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', '')
            description = info.get('description', '')
            return f"Title: {title}\n\nDescription: {description}"
    except Exception as e:
        print(f"Error fetching transcript: {e}")    
        return None

@app.route("/")
def home():
    return render_template("index2.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    url = request.json.get("url")

    if not url:
        return jsonify({"result": "No URL provided"})

    video_text = get_transcript(url)

    if not video_text:
        return jsonify({"result": "Could not fetch video. Try a different link!"})

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