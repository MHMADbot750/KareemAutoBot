import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    await update.message.reply_text("⏳ جاري التحميل...")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best',
        'quiet': True,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(file_name, 'rb'))

        os.remove(file_name)

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

app.run_polling()
