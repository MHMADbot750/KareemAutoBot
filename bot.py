import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    await update.message.reply_text("⏳ جاري التحميل...")

    try:

        ydl_opts = {
            "format": "best",
            "outtmpl": "video.mp4",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # إرسال الفيديو
        if os.path.exists("video.mp4"):
            with open("video.mp4", "rb") as f:
                await update.message.reply_video(f)

        # استخراج الصوت
        os.system('ffmpeg -i video.mp4 -q:a 0 -map a audio.mp3')

        if os.path.exists("audio.mp3"):
            with open("audio.mp3", "rb") as f:
                await update.message.reply_audio(f)

        # تنظيف السيرفر
        os.remove("video.mp4")
        os.remove("audio.mp3")

    except Exception as e:
        await update.message.reply_text("❌ فشل التحميل")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

print("Bot running...")

app.run_polling()
