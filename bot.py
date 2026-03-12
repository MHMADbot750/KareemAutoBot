import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:

        # تحميل الفيديو
        video_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": "video.mp4",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])

        # إرسال الفيديو
        with open("video.mp4", "rb") as f:
            await update.message.reply_video(f)

        os.remove("video.mp4")

        # تحميل الصوت
        audio_opts = {
            "format": "bestaudio/best",
            "outtmpl": "audio.%(ext)s",
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]
        }

        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])

        # إرسال الصوت
        with open("audio.mp3", "rb") as f:
            await update.message.reply_audio(f)

        os.remove("audio.mp3")

        await msg.delete()

    except Exception as e:
        await msg.edit_text("❌ فشل التحميل")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot started")

app.run_polling()
