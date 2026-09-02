#!/usr/bin/env python3
"""
Telegram Bot Template — multi-source API with inline keyboards.
Replace BOT_TOKEN and add/remove handlers as needed.
"""

import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Multi-source fetcher ──

def try_source_a():
    """First API source"""
    try:
        r = requests.get("https://api.example.com/data", timeout=8,
                         headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            d = r.json()
            return {"key": d.get("value"), "source": "source_a"}
    except Exception as e:
        logger.warning(f"source_a: {e}")
    return None


def try_source_b():
    """Fallback API source"""
    try:
        r = requests.get("https://backup.example.com/data", timeout=8,
                         headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            d = r.json()
            return {"key": d.get("result"), "source": "source_b"}
    except Exception as e:
        logger.warning(f"source_b: {e}")
    return None


def get_data():
    """Try all sources, return first successful"""
    for fn in [try_source_a, try_source_b]:
        try:
            result = fn()
            if result and result.get("key"):
                return result
        except Exception:
            continue
    return {}


def fmt(price):
    """Format number with commas"""
    try:
        return f"{int(float(str(price).replace(',', ''))):,}"
    except (ValueError, TypeError):
        return "N/A"


def build_message(data):
    """Build formatted message"""
    now = datetime.now().strftime("%Y/%m/%d  %H:%M")
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊  Data: {fmt(data.get('key'))}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐  {now}\n"
        f"📡  {data.get('source', 'N/A')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )


# ── Handlers ──

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔄  Refresh", callback_data="refresh")],
    ]
    await update.message.reply_text(
        "👋 Welcome!\n\nPress refresh to get data:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("⏳  Loading...")
    data = get_data()
    msg = build_message(data) if data else "❌  Error"
    kb = [[InlineKeyboardButton("🔄  Refresh", callback_data="refresh")]]
    await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb))


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commands:\n/start - Start\n/help - Help")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(refresh_callback))
    print("✅  Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
