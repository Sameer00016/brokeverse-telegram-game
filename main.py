import json, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import *
from levels import LEVELS
from security import anti_tap, can_claim

# ---------- DATABASE ----------
def load_db():
    try:
        with open("database.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_db():
    with open("database.json", "w") as f:
        json.dump(DB, f)

DB = load_db()

# ---------- USER INIT ----------
def get_user(uid):
    if str(uid) not in DB:
        DB[str(uid)] = {
            "points": 0,
            "level": 1,
            "tap_power": 1,
            "last_claim": 0,
            "warnings": 0,
            "banned": False
        }
    return DB[str(uid)]

# ---------- LEVEL CHECK ----------
def update_level(user):
    for lvl, req in LEVELS.items():
        if user["points"] >= req:
            user["level"] = lvl

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_user(update.effective_user.id)
    save_db()

    kb = [
        [InlineKeyboardButton("👆 TAP", callback_data="tap")],
        [InlineKeyboardButton("🎁 Daily Claim", callback_data="claim")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")]
    ]

    await update.message.reply_text(
        "🔥 Welcome to BROKEVERSE\nTap your way out of poverty.",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ---------- TAP ----------
async def tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = get_user(q.from_user.id)

    if user["banned"]:
        await q.answer("⛔ You are banned.")
        return

    if not anti_tap(user):
        await q.answer("⚠️ Slow down.")
        save_db()
        return

    user["points"] += user["tap_power"]
    update_level(user)
    save_db()

    await q.answer(f"+{user['tap_power']} points")

# ---------- CLAIM ----------
async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = get_user(q.from_user.id)

    if not can_claim(user):
        await q.answer("⏳ Come back tomorrow.")
        return

    reward = user["level"] * 1000
    user["points"] += reward
    user["last_claim"] = time.time()
    update_level(user)
    save_db()

    await q.answer(f"🎁 You claimed {reward} points!")

# ---------- LEADERBOARD ----------
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query

    top = sorted(DB.items(), key=lambda x: x[1]["points"], reverse=True)[:5]
    text = "🏆 Leaderboard\n\n"
    for i, (uid, u) in enumerate(top, 1):
        text += f"{i}. {u['points']} pts\n"

    await q.message.reply_text(text)

# ---------- ROUTER ----------
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    if data == "tap":
        await tap(update, context)
    elif data == "claim":
        await claim(update, context)
    elif data == "leaderboard":
        await leaderboard(update, context)

# ---------- RUN ----------
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(router))

app.run_polling()
