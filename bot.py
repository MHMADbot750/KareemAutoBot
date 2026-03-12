import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtu" not in url:
        await update.message.reply_text("❌ أرسل رابط يوتيوب فقط")
        return

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    ydl_opts = {
        "format": "best[ext=mp4]",
        "outtmpl": "video.%(ext)s",
        "quiet": True,
        "noplaylist": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await msg.delete()

        if os.path.exists(filename):
            with open(filename, "rb") as video:
                await update.message.reply_video(video)

            os.remove(filename)

    except Exception as e:
        await msg.edit_text(f"❌ فشل التحميل\n{e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot started")
app.run_polling()
