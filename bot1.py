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

# ✅ Create manual asyncio loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def start_bot():
    await application.initialize()
    await application.start()
    print("✅ Application started and handlers are live.")

# 🔥 Run the startup coroutine BEFORE Flask starts
loop.run_until_complete(start_bot())

# ✅ Root route
@app.route("/")
def home():
    return "✅ Bot is running on Render!"

# ✅ Webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("✅ Telegram POST received:", data)

    update = Update.de_json(data, application.bot)
    asyncio.run_coroutine_threadsafe(application.process_update(update), loop)

    return "ok"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ /start triggered")
    await update.message.reply_text("Hello! The bot is alive and NOW replying correctly.")

# 🛠 Handlers
application.add_handler(CommandHandler("start", start))

# 🚀 Run Flask server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("✅ Bot is starting on Render webhook...")
    app.run(host="0.0.0.0", port=port)
