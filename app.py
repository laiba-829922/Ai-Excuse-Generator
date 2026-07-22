import os
import time

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai


# ================= LOAD ENV =================

load_dotenv()

app = Flask(__name__)


# ================= ENV VARIABLES =================

api_key = os.getenv("GEMINI_API_KEY")
WEB3FORMS_ACCESS_KEY = os.getenv("WEB3FORMS_ACCESS_KEY")


if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

if not WEB3FORMS_ACCESS_KEY:
    raise ValueError("WEB3FORMS_ACCESS_KEY not found")


# ================= GEMINI CLIENT =================

client = genai.Client(api_key=api_key)


# ================= HOME PAGE =================

@app.route("/")
def home():
    return render_template("index.html")


# ================= ABOUT PAGE =================

@app.route("/about")
def about():
    return render_template("about.html")


# ================= CONTACT PAGE =================

@app.route("/contact")
def contact():

    success = request.args.get("success")

    return render_template(
        "contact.html",
        web3forms_key=WEB3FORMS_ACCESS_KEY,
        success=(
            "Your message has been sent successfully."
            if success == "1"
            else None
        )
    )


# ================= FAQ PAGE =================

@app.route("/faq")
def faq():
    return render_template("faq.html")


# ================= AI GENERATOR =================

@app.route("/generate", methods=["POST"])
def generate_excuse():

    data = request.get_json(silent=True) or {}

    situation = str(data.get("situation", "")).strip()
    category = str(data.get("category", "general")).strip()
    tone = str(data.get("tone", "serious")).strip()
    language = str(data.get("language", "roman-urdu")).strip()
    length = str(data.get("length", "short")).strip()

    if not situation:
        return jsonify({
            "error": "Please write your situation first."
        }), 400

    prompt = f"""
Generate one natural, believable, and realistic excuse.

Situation: {situation}
Category: {category}
Tone: {tone}
Language: {language}
Length: {length}

Rules:
- Return only the excuse.
- Do not include a title, heading, explanation, or quotation marks.
- If length is short, write exactly 1 sentence.
- If length is medium, write 2 to 3 sentences.
- If length is long, write 4 to 5 sentences.
- Make it sound natural and human-written.
- Match the selected tone and language.
- Avoid repetitive wording.
- Do not help with illegal, dangerous, harmful, or unethical activities.
"""

    models = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite"
    ]

    last_error = None

    for model_name in models:

        for attempt in range(3):

            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response.text and response.text.strip():
                    return jsonify({
                        "excuse": response.text.strip()
                    }), 200

            except Exception as error:
                last_error = error

                print(
                    f"Gemini Error | Model: {model_name} | "
                    f"Attempt: {attempt + 1} | {error}"
                )

                if attempt < 2:
                    time.sleep(2 ** attempt)

    print("Final Gemini Error:", last_error)

    return jsonify({
        "error": (
            "AI is temporarily busy. "
            "Please wait a few seconds and try again."
        )
    }), 503


# ================= RUN APP =================

if __name__ == "__main__":
    app.run(debug=True)