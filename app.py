import os
import time

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from groq import Groq


# ================= LOAD ENV =================

load_dotenv()

app = Flask(__name__)


# ================= ENV VARIABLES =================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEB3FORMS_ACCESS_KEY = os.getenv("WEB3FORMS_ACCESS_KEY")


if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found")

if not WEB3FORMS_ACCESS_KEY:
    raise ValueError("WEB3FORMS_ACCESS_KEY not found")


# ================= GROQ CLIENT =================

client = Groq(api_key=GROQ_API_KEY)


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
Generate one safe, natural, believable and realistic excuse.

Situation: {situation}
Category: {category}
Tone: {tone}
Language: {language}
Length: {length}

Follow these rules carefully:

- Return only the excuse.
- Do not include a title, heading, explanation or quotation marks.
- If length is short, write exactly 1 sentence.
- If length is medium, write 2 to 3 sentences.
- If length is long, write 4 to 5 sentences.
- Match the selected category, tone and language.
- Make the wording sound natural and human-written.
- Avoid repetitive or robotic wording.
- Do not create excuses for illegal, dangerous, harmful or unethical activities.
"""

    models = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile"
    ]

    last_error = None

    for model_name in models:

        for attempt in range(3):

            try:
                print(
                    f"Trying Groq model: {model_name} | "
                    f"Attempt: {attempt + 1}"
                )

                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a safe AI excuse generator. "
                                "Follow the user's requested language, "
                                "tone and length. Return only the excuse."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.8,
                    max_tokens=350
                )

                excuse = response.choices[0].message.content

                if excuse and excuse.strip():
                    return jsonify({
                        "excuse": excuse.strip()
                    }), 200

            except Exception as error:
                last_error = error

                print(
                    f"Groq Error | Model: {model_name} | "
                    f"Attempt: {attempt + 1} | {error}"
                )

                if attempt < 2:
                    time.sleep(2 ** attempt)

    print("Final Groq Error:", last_error)

    return jsonify({
        "error": (
            "AI is temporarily busy. "
            "Please wait a few seconds and try again."
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
    print("Internal Server Error:", error)

    return jsonify({
        "error": "Something went wrong. Please try again."
    }), 500


# ================= RUN APP =================

if __name__ == "__main__":
    app.run(debug=True)