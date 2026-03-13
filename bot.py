import os
import yt_dlp
import subprocess
import threading
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# تحديث yt-dlp تلقائي
def auto_update():
    while True:
        try:
            subprocess.run(["pip","install","-U","yt-dlp"])
            print("yt-dlp updated")
        except:
            print("update failed")

        time.sleep(43200)

threading.Thread(target=auto_update, daemon=True).start()


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:

        video_opts = {
            "format": "best[filesize<50M]",
            "outtmpl": "video.mp4",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])

        if os.path.exists("video.mp4"):

            with open("video.mp4","rb") as f:
                await update.message.reply_video(f)

            os.remove("video.mp4")

        audio_opts = {
            "format": "bestaudio/best",
            "outtmpl": "audio.%(ext)s",
            "postprocessors":[{
                "key":"FFmpegExtractAudio",
                "preferredcodec":"mp3",
                "preferredquality":"192"
            }]
        }

        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])

        if os.path.exists("audio.mp3"):

            with open("audio.mp3","rb") as f:
                await update.message.reply_audio(f)

            os.remove("audio.mp3")

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ فشل التحميل\n{e}")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot Running")

app.run_polling()
