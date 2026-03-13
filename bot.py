import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:

        # تحميل الفيديو
        video_opts = {
            "format": "best",
            "outtmpl": "video.mp4",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])

        with open("video.mp4", "rb") as f:
            await update.message.reply_video(f)

        os.remove("video.mp4")

        # تحميل الصوت مباشرة
        audio_opts = {
            "format": "bestaudio",
            "outtmpl": "audio.m4a",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])

        with open("audio.m4a", "rb") as f:
            await update.message.reply_audio(f)

        os.remove("audio.m4a")

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ فشل التحميل\n{e}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot started")

app.run_polling()
