import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    loading = await update.message.reply_text("🐿️ جاري تحميل الفيديو...")

    video_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": "video.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "geo_bypass": True
    }

    audio_opts = {
        "format": "bestaudio/best",
        "outtmpl": "audio.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    }

    try:
        # تحميل الفيديو
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info)

        # تحميل الصوت
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.extract_info(url, download=True)

        audio_file = "audio.mp3"

        await loading.delete()

        if os.path.exists(video_file):
            with open(video_file, "rb") as v:
                await update.message.reply_video(v)

        if os.path.exists(audio_file):
            with open(audio_file, "rb") as a:
                await update.message.reply_audio(a)

        if os.path.exists(video_file):
            os.remove(video_file)

        if os.path.exists(audio_file):
            os.remove(audio_file)

    except Exception as e:
        await loading.edit_text(f"❌ فشل التحميل\n{e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot started")
app.run_polling()
