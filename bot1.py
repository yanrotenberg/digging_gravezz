from flask import Flask, request
import os
import logging
import requests

# ✅ Logging
logging.basicConfig(level=logging.INFO)

# 🔑 Token
TOKEN = os.environ.get("BOT_TOKEN", "8099152653:AAE9cUupvk4etyIg8rh4Zsx2jaiN8kb8J70")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# 🌐 Flask app
app = Flask(__name__)

# ✅ Root route
@app.route("/")
def home():
    return "✅ Bot is running on Render!"

# ✅ Webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logging.info(f"✅ Telegram POST received: {data}")

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "✅ Hello! This is the simplest webhook bot possible."
            })

    return "ok"
    
# 🚀 Run Flask server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
