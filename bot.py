import os
import time
import asyncio
import yt_dlp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

LOADING_STICKER = "CAACAgIAAxkBAAIBQ2X"

user_limits = {}


# تنظيف ملفات السيرفر
def clean_files():
    for f in os.listdir():
        if f.endswith((".mp4", ".mp3", ".webm", ".mkv")):
            try:
                os.remove(f)
            except:
                pass


# حد الاستخدام
def check_limit(user_id):

    now = time.time()

    data = user_limits.get(user_id)

    if not data:
        user_limits[user_id] = {"count": 0, "time": now}
        data = user_limits[user_id]

    if now - data["time"] > 86400:
        data["count"] = 0
        data["time"] = now

    if data["count"] >= 10:
        return False

    data["count"] += 1
    return True


# تحميل الفيديو
def download_video(url, filename, fmt):

    ydl_opts = {
        "format": fmt,
        "outtmpl": filename,
        "quiet": True,
        "noplaylist": True,
        "retries": 10
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "أرسل رابط YouTube أو TikTok\n"
        "YouTube : اختيار الدقة\n"
        "TikTok : فيديو + صوت"
    )


# استقبال الرابط
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    user_id = update.message.from_user.id

    if not check_limit(user_id):

        await update.message.reply_text(
            "❌ وصلت الحد اليومي 10 تنزيلات\nارجع بعد 24 ساعة"
        )

        return
