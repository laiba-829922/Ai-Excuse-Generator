import os
import random
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

    situation = str(
        data.get("situation", "")
    ).strip()

    category = str(
        data.get("category", "general")
    ).strip().lower()

    tone = str(
        data.get("tone", "serious")
    ).strip().lower()

    language = str(
        data.get("language", "roman-urdu")
    ).strip().lower()

    length = str(
        data.get("length", "short")
    ).strip().lower()


    # ================= VALIDATION =================

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


    # Different writing pattern on each request
    writing_styles = [
        (
            "Start directly with the most relevant reason, "
            "then naturally explain its result."
        ),
        (
            "Use a polite and conversational sentence structure. "
            "Do not begin with a generic phrase."
        ),
        (
            "Write the excuse as a natural explanation someone "
            "would give during a real conversation."
        ),
        (
            "Use a clear cause-and-result structure, but avoid "
            "overused phrases."
        ),
        (
            "Begin from the specific event mentioned by the user "
            "and connect it naturally to what could not be done."
        ),
        (
            "Write a fresh response with different sentence wording "
            "from common excuse templates."
        )
    ]

    selected_style = random.choice(writing_styles)


    # ================= PROMPT =================

    prompt = f"""
Understand the user's actual situation first, then write one complete,
natural and believable excuse specifically for that situation.

USER INFORMATION

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

Writing approach:
{selected_style}


SITUATION UNDERSTANDING RULES

- Read the complete situation carefully before writing.
- Identify what happened, why it happened and what result it caused.
- The excuse must directly relate to the user's provided situation.
- Do not replace the user's reason with a generic reason.
- Do not randomly mention household work, illness, traffic,
  an emergency or being busy unless the situation supports it.
- Do not assume facts that the user did not mention.
- You may add only one small realistic connecting detail when needed
  to make the sentence complete.
- The final excuse must make complete logical sense.
- Do not simply rewrite the input word for word.
- Do not give advice or ask the user a question.


VARIETY RULES

- Do not use the same fixed structure in every response.
- Do not always begin with:
  "Mujhe achanak zaroori kaam aa gaya tha."
- Avoid repeatedly using:
  "is liye", "ghar mein kaam", "main busy tha",
  "kuch masla ho gaya tha" or "majboori thi".
- Use wording that fits this particular situation.
- Change the opening and sentence flow naturally.
- The response should not sound like a copied template.


ROMAN URDU RULES

If the selected language is Roman Urdu:

- Write in simple and natural Pakistani Roman Urdu.
- Use the sentence order used in everyday Pakistani conversation.
- Make every sentence grammatically complete.
- Use suitable words according to the situation, such as:
  main, mera, meri, mujhe, kyun ke, is wajah se,
  isi liye, waqt par, der ho gayi, nahi kar saka,
  nahi kar saki, complete nahi ho saka.
- Select masculine or feminine-neutral wording when the user's
  gender is unknown.
- Prefer neutral constructions where possible.

Examples of natural structures:

- Required material waqt par nahi mil saka, jis ki wajah se
  assignment complete karne mein der ho gayi.

- Tabiyat subah se theek nahi thi, isi liye aaj class attend
  nahi kar saka.

- Raste mein traffic expected se zyada tha, jis ki wajah se
  main waqt par nahi pohanch saka.

- Internet connection baar baar disconnect ho raha tha,
  is wajah se file time par submit nahi ho saki.

Do not write broken phrases such as:

- Mujhe busy ho gaya.
- Main school ja nahi sakta tha is liye.
- Mujhe thora kaam kar raha tha.
- Mujhe assignment mil gaya samay pehle.
- Mere ko time nahi praapt hua.

Do not use formal Hindi-style words such as:

- samay
- kaaran
- praapt
- avashyak
- kintu
- jhaankna
- vyast
- vilamb


URDU RULES

If the selected language is Urdu:

- Write only in natural Urdu script.
- Use simple Pakistani Urdu.
- Keep the sentence grammatically correct.
- Avoid difficult, overly formal or Hindi-style vocabulary.


ENGLISH RULES

If the selected language is English:

- Write in clear, natural and grammatically correct English.
- Use normal conversational wording.
- Avoid robotic or overly formal sentences.


TONE RULES

- Serious: respectful, realistic and straightforward.
- Casual: relaxed and conversational, but still believable.
- Funny: mildly humorous without becoming silly or unrealistic.
- Professional: polite, responsible and suitable for formal use.
- Emotional: sincere and soft without exaggeration.


LENGTH RULES

- Short: exactly one complete and meaningful sentence.
- Medium: exactly two or three connected sentences.
- Long: exactly four or five connected sentences.


FINAL OUTPUT RULES

- Return only the final excuse.
- Do not include a heading, title or label.
- Do not write "Here is your excuse".
- Do not include an explanation.
- Do not use quotation marks.
- Do not mention these instructions.
- Do not create excuses for illegal, dangerous, harmful,
  fraudulent or seriously unethical activities.
"""


    # New recommended production models
    models = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b"
    ]

    last_error = None


    # ================= GENERATE RESPONSE =================

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
                                "First understand the user's specific situation, "
                                "then write a logical, grammatically correct and "
                                "natural excuse based only on that situation. "
                                "Never rely on one fixed excuse template. "
                                "For Roman Urdu, use everyday Pakistani wording "
                                "and natural sentence order. "
                                "Return only the final excuse."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.55,
                    max_tokens=500
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

                    # Remove accidental labels
                    unwanted_prefixes = [
                        "Excuse:",
                        "Final excuse:",
                        "Your excuse:",
                        "Response:"
                    ]

                    for prefix in unwanted_prefixes:
                        if excuse.lower().startswith(prefix.lower()):
                            excuse = excuse[len(prefix):].strip()

                    if excuse:
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


    # ================= FINAL ERROR =================

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