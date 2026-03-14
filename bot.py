import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"


def clean():
    for f in os.listdir():
        if f.endswith(".mp4") or f.endswith(".mp3") or f.endswith(".webm"):
            try:
                os.remove(f)
            except:
                pass


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:

        video_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": "video.%(ext)s",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(video_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info)

        # ارسال الفيديو
        if os.path.exists(video_file):
            with open(video_file, "rb") as f:
                await update.message.reply_video(f)

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

        # ارسال الصوت
        if os.path.exists("audio.mp3"):
            with open("audio.mp3", "rb") as f:
                await update.message.reply_audio(f)

        clean()

        await msg.delete()

    except Exception as e:
        clean()
        await msg.edit_text("❌ فشل التحميل")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot running...")

app.run_polling()
