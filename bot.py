from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp
import os

# التوكن جاهز
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,  # لتجنب قوائم التشغيل
        'quiet': True,       # لإخفاء أي رسائل في الخلفية
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)

        # إرسال الفيديو أو الصوت مباشرة مع رمز الطائر 🕊️
        if os.path.exists(filename):
            if filename.endswith(".mp3"):
                await update.message.reply_audio(audio=open(filename, "rb"), caption="🕊️")
            else:
                await update.message.reply_video(video=open(filename, "rb"), caption="🕊️")

        # حذف الملف بعد الإرسال
        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

# إعداد البوت وتشغيله
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.run_polling()
