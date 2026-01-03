# pip install Flask google-generativeai
# https://aistudio.google.com/app/api-keys
# GOOGLE_API_KEY

import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = None
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)

GEMINI_MODEL_NAME = "gemini-2.5-flash"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({"error": "Google API kulcs hiányzik."}), 500

    data = request.get_json()
    full_history = data.get('history', [])

    if not full_history:
        return jsonify({"error": "Üres üzenet."}), 400

    try:
        formatted_history = []
        past_messages = full_history[:-1]
        last_message_text = full_history[-1]['parts'][0]

        for msg in past_messages:
            formatted_history.append(types.Content(
                role=msg['role'],
                parts=[types.Part.from_text(text=msg['parts'][0])]
            ))

        chat = client.chats.create(
            model=GEMINI_MODEL_NAME,
            history=formatted_history
        )

        response = chat.send_message(last_message_text)

        return jsonify({"response": response.text})

    except Exception as e:
        print(f"Hiba: {e}")
        return jsonify({"error": f"Hiba történt: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
