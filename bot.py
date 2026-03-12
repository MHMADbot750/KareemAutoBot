import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "ضع_توكن_البوت_هنا"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # نقبل روابط يوتيوب فقط
    if "youtu" not in url:
        await update.message.reply_text("❌ أرسل رابط يوتيوب فقط")
        return

    msg = await update.message.reply_text("⏳ جاري تحميل فيديو يوتيوب...")

    # نحاول أخذ mp4 جاهز مع الصوت (لا يحتاج FFmpeg)
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": "video.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "extractor_args": {
            "youtube": {"player_client": ["android", "web"]}
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0"
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await msg.delete()

        if os.path.exists(filename):
            with open(filename, "rb") as f:
                await update.message.reply_video(f)
            os.remove(filename)
        else:
            await update.message.reply_text("❌ لم يتم العثور على الملف بعد التحميل")

    except Exception as e:
        await msg.edit_text(f"❌ فشل التحميل\n{e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot started")
app.run_polling()
