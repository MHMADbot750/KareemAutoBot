import os
import subprocess
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": "video.mp4",
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # ارسال الفيديو
        with open("video.mp4", "rb") as f:
            await update.message.reply_video(f)

        # استخراج الصوت من الفيديو
        subprocess.run(
            ["ffmpeg", "-i", "video.mp4", "-vn", "-ab", "192k", "-ar", "44100", "-y", "audio.mp3"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # ارسال الصوت
        with open("audio.mp3", "rb") as f:
            await update.message.reply_audio(f)

        os.remove("video.mp4")
        os.remove("audio.mp3")

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ فشل التحميل\n{e}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot started")

app.run_polling()
