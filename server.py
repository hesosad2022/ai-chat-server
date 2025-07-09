from flask import Flask, request, jsonify
import threading
import socket
import requests
import time

# ---------------------------------
# إعدادات API ChatGPT
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct"

# منافذ البروكسي TCP المفتوحة
PROXY_PORTS = [5000, 5001, 5002]

# ---------------------------------
# دالة الاتصال بـ ChatGPT
def call_chatgpt_api(message):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=body, timeout=10)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error from API: {response.status_code}"
    except Exception as e:
        return f"Exception contacting API: {str(e)}"

# ---------------------------------
# معالجة اتصال كل عميل عبر TCP بروكسي
def handle_client(conn, addr):
    print(f"New TCP connection from {addr}")
    try:
        data = conn.recv(4096).decode('utf-8').strip()
        print(f"Received from {addr}: {data}")

        # الاتصال بـ ChatGPT
        reply = call_chatgpt_api(data)
        print(f"Reply to {addr}: {reply}")

        # إرسال الرد للعميل عبر نفس الاتصال
        conn.sendall(reply.encode('utf-8'))
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()

# ---------------------------------
# بدء سيرفر TCP على منفذ معين (بروكسي)
def start_tcp_proxy_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen()
    print(f"TCP Proxy listening on port {port}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

# ---------------------------------
# سيرفر Flask الحالي (مثال بسيط)
app = Flask(__name__)

@app.route("/")
def home():
    return "Main Flask Server Running!"

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    user_message = data.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    reply = call_chatgpt_api(user_message)
    return jsonify({"reply": reply})

# ---------------------------------
if __name__ == "__main__":
    # تشغيل البروكسي TCP على المنافذ المحددة في Threads منفصلة
    for port in PROXY_PORTS:
        threading.Thread(target=start_tcp_proxy_server, args=(port,), daemon=True).start()
import os
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)

