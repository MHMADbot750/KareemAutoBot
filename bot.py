import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ضع توكن بوتك هنا
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:
        # تحميل الفيديو
        video_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": "video.%(ext)s",
            "quiet": True
        }
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info)

        with open(video_file, "rb") as f:
            await update.message.reply_video(f)
        os.remove(video_file)

        # تحميل الصوت (بأي صيغة متاحة)
        audio_opts = {
            "format": "bestaudio/best",
            "outtmpl": "audio.%(ext)s",
            "quiet": True
        }
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(info)

        with open(audio_file, "rb") as f:
            await update.message.reply_audio(f)
        os.remove(audio_file)

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ فشل التحميل\n{e}")

# إنشاء وتشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
print("Bot started")
app.run_polling()
