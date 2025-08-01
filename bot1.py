import os
import time
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# 🔑 Get secrets from environment variables (Render -> Environment tab)
TOKEN = os.environ.get("8326170102:AAGkjxJ1jqOoErRUDUhDPycOJmC58yDjtn4")
URL = os.environ.get("https://your-app.onrender.com")

# 🎮 Game settings
GAME_DURATION = 10   # seconds
CLICK_TARGET = 60    # clicks to win

# 🧠 Store active games per user
games = {}

# 🌐 Flask app for webhook
app = Flask(__name__)

# 🤖 Telegram bot app
application = Application.builder().token(TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Grave Digger mini-game!\nUse /dig to start digging."
    )

# /dig command
async def dig(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    games[user_id] = {"start": time.time(), "clicks": 0}

    # Inline button
    button = InlineKeyboardButton("⛏️ DIG!", callback_data="dig_click")
    keyboard = InlineKeyboardMarkup([[button]])

    # Send shovel image with button
    with open("shovel.png", "rb") as img:
        await update.message.reply_photo(
            photo=img,
            caption=f"⏳ You have {GAME_DURATION} seconds!\n"
                    f"Goal: {CLICK_TARGET} clicks.\nDIG DIG DIG!",
            reply_markup=keyboard
        )

# Handle button clicks
async def handle_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in games:
        await query.answer("No active game. Use /dig to start!")
        return

    game = games[user_id]
    elapsed = time.time() - game["start"]

    if elapsed > GAME_DURATION:
        clicks = game["clicks"]
        del games[user_id]
        if clicks >= CLICK_TARGET:
            await query.message.reply_text("✅ SUCCESS! You dug the grave and trapped the zombies!")
        else:
            await query.message.reply_text(f"❌ FAIL! Only {clicks} clicks. The zombies escaped!")
        await query.answer()
        return

    games[user_id]["clicks"] += 1
    await query.answer(f"Clicks: {games[user_id]['clicks']}")

# 📩 Webhook route for Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK"

# 🌐 Health check
@app.route("/")
def index():
    return "Bot is running!"

# 🔗 Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("dig", dig))
application.add_handler(CallbackQueryHandler(handle_click))

# 🏃 Run on Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"{URL}/{TOKEN}"
    )
    app.run(host="0.0.0.0", port=port)
