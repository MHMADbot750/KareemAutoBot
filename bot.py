import os
import subprocess
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"


def clean():
    for f in os.listdir():
        if f.endswith((".mp4",".mp3",".mkv",".webm",".m4a")):
            try:
                os.remove(f)
            except:
                pass


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    if "tiktok.com" not in url and "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("أرسل رابط TikTok أو YouTube فقط")
        return

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    video_file = "video.mp4"
    audio_file = "audio.mp3"

    try:

        clean()

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": video_file,
            "quiet": True,
            "merge_output_format": "mp4"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(video_file):

            with open(video_file,"rb") as f:
                await update.message.reply_video(f)

            subprocess.run(
                ["ffmpeg","-i",video_file,"-vn","-ab","192k","-ar","44100","-y",audio_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            if os.path.exists(audio_file):
                with open(audio_file,"rb") as f:
                    await update.message.reply_audio(f)

        await msg.delete()

    except Exception as e:

        await msg.edit_text("❌ فشل التحميل")

    finally:

        clean()


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot running...")

app.run_polling()
