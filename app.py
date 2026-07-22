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
    category = str(data.get("category", "general")).strip().lower()
    tone = str(data.get("tone", "serious")).strip().lower()
    language = str(data.get("language", "roman-urdu")).strip().lower()
    length = str(data.get("length", "short")).strip().lower()

    if not situation:
        return jsonify({
            "error": "Please write your situation first."
        }), 400

    if len(situation) > 1000:
        return jsonify({
            "error": (
                "Situation is too long. "
                "Please write a shorter description."
            )
        }), 400

    prompt = f"""
Write one natural and believable excuse based on the information below.

Situation:
{situation}

Category:
{category}

Tone:
{tone}

Language:
{language}

Length:
{length}


ROMAN URDU RULES

If the selected language is Roman Urdu:

- Write in simple, natural Pakistani Roman Urdu.
- The sentence must follow correct and natural word order.
- Write like a real Pakistani person speaking normally.
- Do not translate English into Roman Urdu word by word.
- Use simple words such as:
  main, mera, meri, mujhe, kyun ke, is liye,
  achanak, zaroori, der ho gayi, nahi kar saka.
- Do not use formal Hindi words such as:
  samay, kaaran, praapt, avashyak, kintu or jhaankna.
- Never write grammatically incorrect phrases such as:
  "Mujhe busy ho gaya."
- Write:
  "Main busy ho gaya tha."
  or:
  "Mujhe achanak zaroori kaam aa gaya tha."

Examples of natural Pakistani Roman Urdu:

Incorrect:
Mujhe thora busy ho gaya is liye main school ja nahi sakta.

Correct:
Mujhe achanak zaroori kaam aa gaya tha, is liye main school nahi ja saka.

Incorrect:
Mujhe assignment karne ka samay nahi mila.

Correct:
Mujhe assignment complete karne ka time nahi mil saka.

Incorrect:
Mere ghar mein kaam aa gaya.

Correct:
Ghar mein achanak zaroori kaam aa gaya tha, is liye mujhe rukna pada.


URDU RULES

If the selected language is Urdu:

- Write only in natural Urdu script.
- Use simple Pakistani Urdu.
- Do not use difficult or formal vocabulary.


ENGLISH RULES

If the selected language is English:

- Write in simple and natural English.
- Make the sentence grammatically correct and believable.


LENGTH RULES

- Short: Write exactly one complete sentence.
- Medium: Write exactly two or three complete sentences.
- Long: Write exactly four or five complete sentences.


FINAL RULES

- Return only the final excuse.
- Do not include a heading, title, label or explanation.
- Do not use quotation marks.
- Match the selected category and tone.
- Do not copy the user's situation word for word.
- Do not add random or confusing details.
- The result must be grammatically correct.
- The result must have a clear sentence sequence.
- Make it natural, believable and human-written.
- Do not create excuses for illegal, dangerous, harmful,
  fraudulent or seriously unethical activities.
"""

    models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
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
                                "You are an expert Pakistani language writer. "
                                "Create grammatically correct, naturally "
                                "ordered and believable excuses. When Roman "
                                "Urdu is selected, use simple everyday "
                                "Pakistani Roman Urdu. Never use broken "
                                "sentences, formal Hindi words or literal "
                                "translations. Return only the final excuse."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.25,
                    max_tokens=400
                )

                if not response.choices:
                    continue

                excuse = response.choices[0].message.content

                if excuse and excuse.strip():

                    excuse = excuse.strip()

                    # Remove accidental quotation marks
                    excuse = excuse.strip('"')
                    excuse = excuse.strip("'")
                    excuse = excuse.strip()

                    return jsonify({
                        "excuse": excuse
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