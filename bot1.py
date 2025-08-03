from flask import Flask, request
import os
import logging
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

# ✅ Logging
logging.basicConfig(level=logging.INFO)

# 🔑 Token
TOKEN = os.environ.get("BOT_TOKEN", "8099152653:AAE9cUupvk4etyIg8rh4Zsx2jaiN8kb8J70")
bot = Bot(token=TOKEN)

# 🌐 Flask app
app = Flask(__name__)

# ✅ Dispatcher (sync version)
dispatcher = Dispatcher(bot, None, workers=0)

# /start command
def start(update: Update, context):
    chat_id = update.effective_chat.id
    bot.send_message(chat_id=chat_id, text="✅ Hello! This is a minimal webhook bot.")

# Add handler
dispatcher.add_handler(CommandHandler("start", start))

# ✅ Root route
@app.route("/")
def home():
    return "✅ Bot is running on Render!"

# ✅ Webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, bot)
    dispatcher.process_update(update)
    return "ok"

# 🚀 Run Flask server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
