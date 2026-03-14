import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"


def clean():
    for f in os.listdir():
        if f.endswith((".mp4", ".mp3", ".webm", ".mkv")):
            try:
                os.remove(f)
            except:
                pass


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:

        clean()

        # تحميل الفيديو
        ydl_opts = {
            "format": "best",
            "outtmpl": "video.mp4",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # ارسال الفيديو
        if os.path.exists("video.mp4"):
            with open("video.mp4", "rb") as f:
                await update.message.reply_video(f)

        # استخراج الصوت
        os.system("ffmpeg -i video.mp4 -vn -ab 192k audio.mp3")

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
