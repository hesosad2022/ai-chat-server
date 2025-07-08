from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Requests

# Get API key from environment variables (NEVER hardcode)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Validate input
        user_msg = request.json.get("message", "")
        if not user_msg.strip():
            return jsonify({"error": "Message cannot be empty"}), 400

        # Call OpenRouter API
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://yourdomain.com",  # OpenRouter requires this
            },
            json={
                "model": "openchat/openchat-3.5",
                "messages": [{"role": "user", "content": user_msg}]
            },
            timeout=10  # Prevent hanging requests
        )

        response.raise_for_status()  # Raise HTTP errors
        ai_response = response.json()
        reply = ai_response["choices"][0]["message"]["content"]
        
        return jsonify({"reply": reply})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 502
    except KeyError:
        return jsonify({"error": "Invalid API response format"}), 502
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Server running on port {port}")
    app.run(host="0.0.0.0", port=port)
