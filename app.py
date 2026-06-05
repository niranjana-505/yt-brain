from dotenv import load_dotenv
import os
import re
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

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


def get_transcript(url):
    video_id = get_video_id(url)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            transcript = transcript_list.find_generated_transcript(['en'])

        data = transcript.fetch()

        return " ".join([item["text"] for item in data])

    except:
        return None


@app.route("/")
def home():
    return render_template("index2.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        url = request.json.get("url")

        if not url:
            return jsonify({"result": "No URL provided"})

        video_text = get_transcript(url)

        if not video_text:
            return jsonify({"result": "Transcript unavailable for this video"})

        prompt = f"""
Based on this YouTube video transcript, give:

1. A short summary (4–15 sentences)
2. 5 key bullet points
3. 5 quiz questions with answers

No markdown. No asterisks. Plain text only.

Transcript:
{video_text[:8000]}
"""

        response = model.generate_content(prompt)

        return jsonify({"result": response.text})

    except:
        return jsonify({"result": "Server error occurred"})


if __name__ == "__main__":
    app.run(debug=True)