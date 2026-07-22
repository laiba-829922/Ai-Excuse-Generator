import os
import smtplib

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ================= LOAD ENV =================

load_dotenv()

app = Flask(__name__)


# ================= ENV VARIABLES =================

api_key = os.getenv("GEMINI_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

if not EMAIL_USER or not EMAIL_PASS:
    raise ValueError("EMAIL_USER or EMAIL_PASS not found")


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
            email_message = MIMEMultipart()

            email_message["From"] = EMAIL_USER
            email_message["To"] = EMAIL_USER
            email_message["Reply-To"] = email
            email_message["Subject"] = "New Contact Message - ExcuseAI"

            body = f"""
New message received from ExcuseAI contact form.

Name: {name}
Email: {email}

Message:
{message}
"""

            email_message.attach(
                MIMEText(body, "plain")
            )

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()

                server.login(
                    EMAIL_USER,
                    EMAIL_PASS
                )

                server.send_message(
                    email_message
                )

            return render_template(
                "contact.html",
                success="Your message has been sent successfully."
            )

        except Exception as error:
            print("Contact Email Error:", error)

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
            "error": "AI response not found."
        }), 500


# ================= RUN APP =================

if __name__ == "__main__":
    app.run(debug=True)