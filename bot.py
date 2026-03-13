import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# تحديث المكتبة تلقائياً
os.system("pip install -U yt-dlp")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("⏳ جاري التحميل...")

    ydl_opts = {
        "format": "best",
        "outtmpl": "video.%(ext)s",
        "retries": 10,
        "fragment_retries": 10,
        "quiet": True,
        "noplaylist": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(filename, "rb"))
        os.remove(filename)

    except Exception as e:
        # إصلاح تلقائي إذا حصل خطأ
        os.system("pip install -U yt-dlp")
        await update.message.reply_text(f"⚠️ حصل خطأ وتم محاولة الإصلاح:\n{e}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot is running...")
app.run_polling()
