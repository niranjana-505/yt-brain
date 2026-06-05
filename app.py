from dotenv import load_dotenv
import os
import re
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound
)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Gemini setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


# Extract YouTube video ID
def get_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None


# Get transcript safely
def get_transcript(url):
    video_id = get_video_id(url)

    if not video_id:
        return None

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])

    except TranscriptsDisabled:
        return None

    except NoTranscriptFound:
        return None

    except Exception:
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
            return jsonify({"result": "Transcript unavailable for this video 😔"})

        prompt = f"""
Based on this YouTube video transcript, give me:

1. A short summary (4–15 sentences)
2. 5 key bullet points
3. 5 quiz questions with answers

Reply in plain text only. No markdown, no hashtags, no asterisks.

Transcript:
{video_text[:8000]}
"""

        response = model.generate_content(prompt)

        return jsonify({"result": response.text})

    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True)     