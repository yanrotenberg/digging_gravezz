from flask import Flask, request
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ✅ Logging
logging.basicConfig(level=logging.INFO)

# 🌐 Flask app
app = Flask(__name__)

# 🔑 Token
TOKEN = os.environ.get("BOT_TOKEN", "8099152653:AAE9cUupvk4etyIg8rh4Zsx2jaiN8kb8J70")
print("DEBUG BOT_TOKEN:", repr(TOKEN))

# 🤖 Telegram Application
application = Application.builder().token(TOKEN).build()

# ✅ Root route
@app.route("/")
def home():
    return "✅ Bot is running on Render!"

# ✅ Webhook route with run_coroutine_threadsafe
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("✅ Telegram POST received:", data)

    update = Update.de_json(data, application.bot)

    # 🔥 Push the update into PTB's asyncio loop manually
    asyncio.run_coroutine_threadsafe(application.process_update(update), application.loop)

    return "ok"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ /start triggered")
    await update.message.reply_text("Hello! The bot is alive and replying now.")

# 🛠 Handler
application.add_handler(CommandHandler("start", start))

# 🚀 Run webhook
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    URL = "https://digging-gravezz.onrender.com"

    print("✅ Bot is starting on Render webhook...")

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"{URL}/{TOKEN}"
    )
