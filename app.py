import os
import time
import random

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
Create one safe, natural, believable and human-written excuse.

Situation: {situation}
Category: {category}
Tone: {tone}
Language: {language}
Length: {length}

Rules:
- Return only the excuse.
- Do not add a title, heading, explanation or quotation marks.
- For short length, write exactly 1 sentence.
- For medium length, write 2 to 3 sentences.
- For long length, write 4 to 5 sentences.
- Follow the selected language and tone.
- Keep the wording natural and non-repetitive.
- Do not create excuses for illegal, dangerous, harmful,
  dishonest or unethical activities.
"""

    models = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-preview-05-20"
]

    last_error = None

    for model_name in models:

        for attempt in range(3):

            try:
                print(
                    f"Trying model: {model_name}, "
                    f"attempt: {attempt + 1}"
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response.text and response.text.strip():

                    excuse = response.text.strip()

                    return jsonify({
                        "excuse": excuse
                    }), 200

            except Exception as error:

                last_error = error

                print(
                    f"Gemini Error | Model: {model_name} | "
                    f"Attempt: {attempt + 1} | {error}"
                )

                if attempt < 2:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)

    print("Final Gemini Error:", last_error)

    return jsonify({
        "error": (
            "AI is temporarily busy. "
            "Please wait a minute and try again."
        )
    }), 503


# ================= ERROR HANDLERS =================

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        "error": "Page not found."
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Something went wrong. Please try again."
    }), 500


# ================= RUN APP =================

if __name__ == "__main__":
    app.run(debug=True)