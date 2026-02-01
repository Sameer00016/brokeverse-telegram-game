import json, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import *
from levels import LEVELS, TAP_UPGRADES, CLAIM_UPGRADES
from security import anti_tap, can_claim

# ---------------- DATABASE ----------------
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

# ---------------- USER ----------------
def get_user(uid):
    if str(uid) not in DB:
        DB[str(uid)] = {
            "points": 0,
            "level": 1,
            "tap_level": 1,
            "claim_level": 1,
            "last_claim": 0,
            "warnings": 0,
            "banned": False
        }
    return DB[str(uid)]

# ---------------- LEVELS ----------------
def update_level(user):
    for lvl, req in LEVELS.items():
        if user["points"] >= req:
            user["level"] = lvl

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_user(update.effective_user.id)
    save_db()
    kb = [
        [InlineKeyboardButton("👆 TAP", callback_data="tap")],
        [InlineKeyboardButton("🎁 Daily Claim", callback_data="claim")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("🔧 Upgrade Tap", callback_data="upgrade_tap")],
        [InlineKeyboardButton("💎 Upgrade Claim", callback_data="upgrade_claim")],
    ]
    await update.message.reply_text(
        "🔥 Welcome to BROKEVERSE\nTap, Claim, Upgrade & reach luxury!",
        reply_markup=InlineKeyboardMarkup(kb)
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
    reward = CLAIM_UPGRADES.get(user["claim_level"], user["level"]*1000)
    user["points"] += reward
    user["last_claim"] = time.time()
    update_level(user)
    save_db()
    await q.answer(f"🎁 You claimed {reward} points!")

# ---------------- LEADERBOARD ----------------
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    top = sorted(DB.items(), key=lambda x: x[1]["points"], reverse=True)[:10]
    text = "🏆 Leaderboard\n\n"
    for i, (uid, u) in enumerate(top, 1):
        text += f"{i}. {u['points']} pts (Lvl {u['level']})\n"
    await q.message.reply_text(text)

# ---------------- UPGRADE TAP ----------------
async def upgrade_tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = get_user(q.from_user.id)
    if user["tap_level"] >= 50:
        await q.answer("Max tap level reached!")
        return
    cost = (user["tap_level"]*500)  # points cost
    if user["points"] < cost:
        await q.answer(f"Not enough points! Need {cost}")
        return
    user["points"] -= cost
    user["tap_level"] += 1
    save_db()
    await q.answer(f"Tap upgraded to {user['tap_level']}!")

# ---------------- UPGRADE CLAIM ----------------
async def upgrade_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = get_user(q.from_user.id)
    if user["claim_level"] >= 50:
        await q.answer("Max claim level reached!")
        return
    cost = (user["claim_level"]*500)  # points cost
    if user["points"] < cost:
        await q.answer(f"Not enough points! Need {cost}")
        return
    user["points"] -= cost
    user["claim_level"] += 1
    save_db()
    await q.answer(f"Claim upgraded to {user['claim_level']}!")

# ---------------- ROUTER ----------------
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    if data == "tap": await tap(update, context)
    elif data == "claim": await claim(update, context)
    elif data == "leaderboard": await leaderboard(update, context)
    elif data == "upgrade_tap": await upgrade_tap(update, context)
    elif data == "upgrade_claim": await upgrade_claim(update, context)

# ---------------- RUN ----------------
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found in environment variables!")
else:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(router))
    print("✅ BROKEVERSE bot started successfully!")
    app.run_polling()
