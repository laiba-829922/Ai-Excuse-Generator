import os
import requests

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

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            return render_template(
                "contact.html",
                error="Please fill all fields."
            )

        try:
            payload = {
                "access_key": WEB3FORMS_ACCESS_KEY,
                "name": name,
                "email": email,
                "subject": "New Contact Message - ExcuseAI",
                "message": message,
                "from_name": "ExcuseAI Contact Form"
            }

            response = requests.post(
                "https://api.web3forms.com/submit",
                json=payload,
                timeout=15
            )

            result = response.json()

            if response.ok and result.get("success"):
                return render_template(
                    "contact.html",
                    success="Your message has been sent successfully."
                )

            print("Web3Forms Error:", result)

            return render_template(
                "contact.html",
                error="Message could not be sent. Please try again."
            )

        except requests.RequestException as error:
            print("Contact Request Error:", error)

            return render_template(
                "contact.html",
                error="Message could not be sent. Please try again."
            )

        except Exception as error:
            print("Contact Error:", error)

            return render_template(
                "contact.html",
                error="Message could not be sent. Please try again."
            )

    return render_template("contact.html")


# ================= FAQ PAGE =================

@app.route("/faq")
def faq():
    return render_template("faq.html")


# ================= AI GENERATOR =================

@app.route("/generate", methods=["POST"])
def generate_excuse():

    data = request.get_json(silent=True) or {}

    situation = data.get("situation", "").strip()
    category = data.get("category", "general")
    tone = data.get("tone", "serious")
    language = data.get("language", "roman-urdu")
    length = data.get("length", "short")

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
You are a professional AI Excuse Generator.

Your job is to create believable, natural, and realistic excuses
that sound human-written.

Always follow the user's selected category, tone, language, and length.

- Return only the excuse.
- Do not include any title, heading, explanation, or quotation marks.
- If the selected length is "short", write exactly 1 sentence.
- If the selected length is "medium", write 2–3 sentences.
- If the selected length is "long", write 4–5 sentences.
- Make the excuse sound natural and convincing.
- Match the selected tone and language.
- Avoid repetitive wording.
- Do not generate excuses for illegal, dangerous, harmful,
  or unethical activities.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        if not response.text:
            return jsonify({
                "error": "AI has generated no response."
            }), 500

        excuse = response.text.strip()

        return jsonify({
            "excuse": excuse
        })

    except Exception as error:
        print("Gemini Error:", error)

        return jsonify({
            "error": "AI response not found. Please try again."
        }), 500


# ================= RUN APP =================

if __name__ == "__main__":
    app.run(debug=True)