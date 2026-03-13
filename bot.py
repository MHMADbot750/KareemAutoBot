import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    if "tiktok.com" not in url:
        await update.message.reply_text("❌ أرسل رابط TikTok فقط")
        return

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:

        # تحميل الفيديو
        video_opts = {
            "format": "best",
            "outtmpl": "video.mp4",
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])

        if os.path.exists("video.mp4"):
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

        if os.path.exists("audio.mp3"):
            with open("audio.mp3", "rb") as f:
                await update.message.reply_audio(f)

            os.remove("audio.mp3")

        await msg.delete()

    except Exception as e:
        print(e)
        await msg.edit_text("❌ فشل التحميل")



app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("TikTok Bot Running")

app.run_polling()
