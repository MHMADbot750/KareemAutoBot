import os
import yt_dlp
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    if "tiktok.com" not in url and "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("أرسل رابط TikTok أو YouTube فقط")
        return

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    video_file = "video.mp4"
    audio_file = "audio.mp3"

    try:

        # تحميل الفيديو
        ydl_opts = {
            "format": "best",
            "outtmpl": video_file,
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # ارسال الفيديو
        if os.path.exists(video_file):
            with open(video_file, "rb") as f:
                await update.message.reply_video(f)

        # استخراج الصوت باستخدام 2
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_file, "-vn", "-acodec", "libmp3lame", "-ab", "192k", audio_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # ارسال الصوت
        if os.path.exists(audio_file):
            with open(audio_file, "rb") as f:
                await update.message.reply_audio(f)

    except Exception as e:
        await update.message.reply_text("❌ فشل التحميل")

    finally:

        # حذف الملفات بعد الإرسال
        if os.path.exists(video_file):
            os.remove(video_file)

        if os.path.exists(audio_file):
            os.remove(audio_file)

        try:
            await msg.delete()
        except:
            pass


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot Running...")

app.run_polling()
