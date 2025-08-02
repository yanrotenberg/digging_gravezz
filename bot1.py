from flask import Flask, request
import os
import time
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# ✅ Logging
logging.basicConfig(level=logging.INFO)

# 🌐 Flask app
app = Flask(__name__)

# 🔑 Token (correct one)
TOKEN = os.environ.get("BOT_TOKEN", "8099152653:AAE9cUupvk4etyIg8rh4Zsx2jaiN8kb8J70")
print("DEBUG BOT_TOKEN:", repr(TOKEN))

# 🎮 Game settings
GAME_DURATION = 10   # seconds
CLICK_TARGET = 30    # digs to win

# 🧠 Active games
games = {}

# 🤖 Telegram Application
application = Application.builder().token(TOKEN).build()

# ✅ Root to check server
@app.route("/")
def home():
    return "✅ Bot is running on Render!"

# ✅ Webhook route using run_coroutine_threadsafe
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("✅ Telegram POST received:", data)

    update = Update.de_json(data, application.bot)

    # 🔥 Schedule the update on PTB's asyncio loop
    asyncio.run_coroutine_threadsafe(application.process_update(update), application.loop)

    return "ok"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ Received /start")
    await update.message.reply_text(
        "Welcome to the Grave Digger mini-game!\nUse /dig to start digging."
    )

# /dig command
async def dig(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    games[user_id] = {"start": time.time(), "clicks": 0}

    await update.message.reply_text(
        f"⏳ You have {GAME_DURATION} seconds!\n"
        f"Goal: {CLICK_TARGET} digs.\n"
        f"Type 'dig' as fast as you can!"
    )

# Count "dig" messages
async def count_digs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    if user_id not in games:
        return

    game = games[user_id]
    elapsed = time.time() - game["start"]

    if elapsed > GAME_DURATION:
        clicks = game["clicks"]
        del games[user_id]
        if clicks >= CLICK_TARGET:
            await update.message.reply_text("✅ SUCCESS! You dug the grave and trapped the zombies!")
        else:
            await update.message.reply_text(f"❌ FAIL! Only {clicks} digs. The walls of the grave are falling! 🧱💀")
        return

    if text == "dig":
        games[user_id]["clicks"] += 1

# 🛠 Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("dig", dig))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_digs))

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
