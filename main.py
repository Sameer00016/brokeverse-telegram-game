import threading
import json
import time
import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import BOT_TOKEN
from levels import LEVELS, TAP_UPGRADES, CLAIM_UPGRADES
from security import anti_tap, can_claim

# ---------------- KEEP ALIVE SERVER ----------------
web = Flask(__name__)

@web.route("/")
def home():
    return "BROKEVERSE BOT RUNNING"

def run_web():
    web.run(host="0.0.0.0", port=8080)

# ---------------- DATABASE ----------------
def load_db():
    try:
        with open("database.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_db():
    try:
        with open("database.json", "w") as f:
            json.dump(DB, f)
    except Exception as e:
        print("DB SAVE ERROR:", e)

DB = load_db()

# ---------------- USER ----------------
def get_user(uid):
    uid = str(uid)
    if uid not in DB:
        DB[uid] = {
            "points": 0,
            "level": 1,
            "tap_level": 1,
            "claim_level": 1,
            "last_claim": 0,
            "warnings": 0,
            "banned": False
        }
    return DB[uid]

# ---------------- LEVEL ----------------
def update_level(user):
    for lvl, req in LEVELS.items():
        if user["points"] >= req:
            user["level"] = lvl

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_user(update.effective_user.id)
    save_db()

    keyboard = [
        [InlineKeyboardButton("👆 TAP", callback_data="tap")],
        [InlineKeyboardButton("🎁 Daily Claim", callback_data="claim")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("🔧 Upgrade Tap", callback_data="upgrade_tap")],
        [InlineKeyboardButton("💎 Upgrade Claim", callback_data="upgrade_claim")]
    ]

    await update.message.reply_text(
        "🔥 Welcome to BROKEVERSE\nTap • Upgrade • Escape Poverty",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- TAP ----------------
async def tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = get_user(q.from_user.id)

    if user["banned"]:
        await q.answer("⛔ You are banned.")
        return

    if not anti_tap(user):
        await q.answer("⚠️ Slow down!")
        save_db()
        return

    points = TAP_UPGRADES.get(user["tap_level"], 1)
    user["points"] += points
    update_level(user)
    save_db()

    await q.answer(f"+{points} points")

# ---------------- CLAIM ----------------
async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = get_user(q.from_user.id)

    if not can_claim(user):
        await q.answer("⏳ Come back tomorrow.")
        return

    reward = CLAIM_UPGRADES.get(user["claim_level"], 1000)
    user["points"] += reward
    user["last_claim"] = time.time()
    update_level(user)
    save_db()

    await q.answer(f"🎁 +{reward} points!")

# ---------------- LEADERBOARD ----------------
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    top = sorted(DB.items(), key=lambda x: x[1]["points"], reverse=True)[:10]

    text = "🏆 Leaderboard\n\n"
    for i, (_, u) in enumerate(top, 1):
        text += f"{i}. {u['points']} pts | Lvl {u['level']}\n"

    await q.message.reply_text(text)

# ---------------- UPGRADES ----------------
async def upgrade_tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = get_user(q.from_user.id)

    if user["tap_level"] >= 50:
        await q.answer("Max tap level!")
        return

    cost = user["tap_level"] * 500
    if user["points"] < cost:
        await q.answer(f"Need {cost} points")
        return

    user["points"] -= cost
    user["tap_level"] += 1
    save_db()

    await q.answer("Tap upgraded!")

async def upgrade_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = get_user(q.from_user.id)

    if user["claim_level"] >= 50:
        await q.answer("Max claim level!")
        return

    cost = user["claim_level"] * 500
    if user["points"] < cost:
        await q.answer(f"Need {cost} points")
        return

    user["points"] -= cost
    user["claim_level"] += 1
    save_db()

    await q.answer("Claim upgraded!")

# ---------------- ROUTER ----------------
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data

    if data == "tap":
        await tap(update, context)
    elif data == "claim":
        await claim(update, context)
    elif data == "leaderboard":
        await leaderboard(update, context)
    elif data == "upgrade_tap":
        await upgrade_tap(update, context)
    elif data == "upgrade_claim":
        await upgrade_claim(update, context)

# ---------------- RUN ----------------
def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(router))
    print("✅ BROKEVERSE BOT STARTED")
    application.run_polling(close_loop=False)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
