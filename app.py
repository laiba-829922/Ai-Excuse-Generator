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
            "error": "Situation is too long. Please write a shorter description."
        }), 400

     prompt = f"""
User ki situation ke mutabiq ek natural aur believable excuse likho.

Situation: {situation}
Category: {category}
Tone: {tone}
Language: {language}
Length: {length}

ROMAN URDU RULES:

Agar language Roman Urdu ho:

- Pakistani everyday Roman Urdu use karo.
- Sentence ka word order bilkul natural hona chahiye.
- Pehle subject, phir situation/reason, phir result likho.
- Grammar correct rakho.
- Past situation mein "tha", "thi", "the", "ho gaya tha",
  "nahi kar saka" ya "nahi kar saki" sahi jagah use karo.
- "Mujhe busy ho gaya" jaisi ghalat wording kabhi mat likho.
- Iski jagah "Main busy ho gaya tha" ya
  "Mujhe zaroori kaam aa gaya tha" likho.
- English se word-by-word translation mat karo.
- Hindi words jaise "samay", "kaaran", "praapt",
  "avashyak" aur "kintu" use mat karo.

NATURAL EXAMPLES:

Wrong:
Mujhe thora busy ho gaya is liye main school ja nahi sakta.

Correct:
Main thora busy ho gaya tha, is liye school nahi ja saka.

Wrong:
Mujhe assignment complete karne mein samay nahi mila.

Correct:
Mujhe assignment complete karne ka time nahi mil saka.

Wrong:
Mere ghar mein kaam aa gaya.

Correct:
Ghar mein achanak zaroori kaam aa gaya tha, is liye mujhe rukna pada.

LENGTH RULES:

- Short: exactly 1 complete and natural sentence.
- Medium: 2 to 3 complete sentences.
- Long: 4 to 5 complete sentences.

FINAL RULES:

- Sirf final excuse return karo.
- Heading, title, explanation ya quotation marks mat lagao.
- Sentence adhura ya grammar ke baghair mat likho.
- Situation ko word-by-word repeat mat karo.
- Excuse simple, realistic aur human-written lagna chahiye.
- Illegal, dangerous ya harmful activity ke liye excuse mat banao.
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
                                "You are an expert Pakistani Roman Urdu writer. "
                                "Write grammatically correct, naturally ordered "
                                "and conversational sentences. Never use broken "
                                "Roman Urdu or literal Hindi-style translation. "
                                "Return only the final excuse."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.35,
                    max_tokens=400
                )

                excuse = response.choices[0].message.content

                if excuse and excuse.strip():

                    excuse = excuse.strip()
                    excuse = excuse.strip('"').strip("'").strip()

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

# ================= RUN APP =================

if __name__ == "__main__":
    app.run(debug=True)