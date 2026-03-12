import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

user_links = {}

async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    user_links[update.message.chat_id] = url

    keyboard = [
        [
            InlineKeyboardButton("📹 تحميل فيديو", callback_data="video"),
            InlineKeyboardButton("🎵 تحميل صوت", callback_data="audio")
        ]
    ]

    await update.message.reply_text(
        "اختر نوع التحميل:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = user_links.get(query.message.chat_id)

    await query.message.edit_text("⏳ جاري التحميل...")

    if query.data == "video":
        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": "video.%(ext)s",
            "quiet": True
        }
    else:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "audio.%(ext)s",
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if query.data == "video":
            with open(filename, "rb") as f:
                await query.message.reply_video(f)
        else:
            mp3 = filename.rsplit(".", 1)[0] + ".mp3"
            with open(mp3, "rb") as f:
                await query.message.reply_audio(f)

        for file in os.listdir():
            if file.startswith("video") or file.startswith("audio"):
                os.remove(file)

    except:
        await query.message.reply_text("❌ فشل التحميل")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_link))
app.add_handler(CallbackQueryHandler(download))

print("Bot started")
app.run_polling()
