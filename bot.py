import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رابط TikTok أو YouTube")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("⏳ جاري التحميل...")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(file, 'rb'))

        audio_file = "audio.mp3"

        os.system(f'ffmpeg -i "{file}" -q:a 0 -map a "{audio_file}"')

        await update.message.reply_audio(audio=open(audio_file, 'rb'))

        os.remove(file)
        os.remove(audio_file)

    except Exception as e:
        await update.message.reply_text("❌ فشل التحميل")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

app.run_polling()
