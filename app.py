from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import yt_dlp
import re

app = Flask(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def get_transcript(url):
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': True,
        'quiet': True,
        'cookiesfile': 'cookies.txt',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Get description as fallback text
        title = info.get('title', '')
        description = info.get('description', '')
        duration = info.get('duration', 0)
        
        return f"Title: {title}\n\nDescription: {description}"

@app.route("/")
def home():
    return render_template("index2.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        url = request.json.get("url")
        video_text = get_transcript(url)
        
        prompt = f"""
        Based on this YouTube video information, give me:
        1. A short summary (4-15 sentences)
        2. 5 key bullet points
        3. 5 quiz questions with answers
        Reply in plain text only. No markdown, no hastags, no asterisks.
        
        Video info: {video_text[:4000]}
        """
        
        response = model.generate_content(prompt)
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)