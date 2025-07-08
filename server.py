
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OPENROUTER_API_KEY = "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"

@app.route("/", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openchat/openchat-3.5",
            "messages": [{"role": "user", "content": user_msg}]
        }
    )

    reply = response.json()["choices"][0]["message"]["content"]
    return jsonify({"reply": reply})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0" , port=port)
