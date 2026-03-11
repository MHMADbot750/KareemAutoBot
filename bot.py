import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ضع توكن البوت هنا
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    loading = await update.message.reply_text("🐿️ جاري تحميل الفيديو...")

    # إعدادات الفيديو
    video_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": "video.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "merge_output_format": "mp4",
        # إذا الفيديو يحتاج كوكيز، ضع مسار ملف cookies.txt هنا
        # "cookiefile": "cookies.txt"
    }

    # إعدادات الصوت
    audio_opts = {
        "format": "bestaudio/best",
        "outtmpl": "audio.%(ext)s",
        "noplaylist": True,
        "quiet": True,
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

        # إرسال الفيديو
        if os.path.exists(video_file):
            with open(video_file, "rb") as v:
                await update.message.reply_video(v, caption="🕊️ تم التحميل!")

        # إرسال الصوت
        if os.path.exists(audio_file):
            with open(audio_file, "rb") as a:
                await update.message.reply_audio(a, caption="🎵 صوت الفيديو")

        # حذف الملفات بعد الإرسال
        if os.path.exists(video_file):
            os.remove(video_file)
        if os.path.exists(audio_file):
            os.remove(audio_file)

    except Exception as e:
        await loading.edit_text(f"❌ فشل تحميل الفيديو: {str(e)}")

# تشغيل البوت
app = ApplicationBuilder().token
