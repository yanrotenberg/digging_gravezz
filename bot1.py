from flask import Flask

app = Flask(__name__)

import os
import time
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# 🔑 Hardcode your token for local testing
TOKEN = "8099152653:AAE9cUupvk4etyIg8rh4Zsx2jaiN8kb8J70"
print("DEBUG BOT_TOKEN:", repr(TOKEN))

# 🎮 Game settings
GAME_DURATION = 10   # seconds
CLICK_TARGET = 30    # digs to win

# 🧠 Store active games: {user_id: {"start": time, "clicks": int}}
games = {}

application = Application.builder().token(TOKEN).build()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Grave Digger mini-game!\nUse /dig to start digging."
    )

# /dig starts the round
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

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("dig", dig))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_digs))

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


from flask import request

@app.route("/")
def home():
    return "✅ Bot is running on Render!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    from telegram import Update
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok"

