# pip install Flask google-generativeai
# https://aistudio.google.com/app/api-keys
# GOOGLE_API_KEY

import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from google.api_core import exceptions

app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

GEMINI_MODEL_NAME = "gemini-2.5-flash"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    if not GOOGLE_API_KEY:
        return jsonify({"error": "Google API kulcs hiányzik."}), 500

    data = request.get_json()
    full_history = data.get('history', [])

    if not full_history:
        return jsonify({"error": "Üres üzenet."}), 400

    try:
        last_message_obj = full_history[-1]
        last_message_text = last_message_obj['parts'][0]
        past_history = full_history[:-1]
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        chat_session = model.start_chat(history=past_history)
        response = chat_session.send_message(last_message_text)
        return jsonify({"response": response.text})

    except exceptions.ResourceExhausted:
        return jsonify({"error": "Kvóta túllépés."}), 429
    except Exception as e:
        print(f"Hiba: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
