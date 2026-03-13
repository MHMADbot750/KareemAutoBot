import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

downloading = False

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global downloading

    url = update.message.text.strip()

    if "tiktok.com" not in url:
        await update.message.reply_text("❌ أرسل رابط TikTok فقط")
        return

    if downloading:
        await update.message.reply_text("⏳ يتم تحميل فيديو آخر انتظر قليلاً")
        return

    downloading = True

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:

        ydl_opts = {
            "format": "best",
            "outtmpl": "video.mp4",
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists("video.mp4"):

            with open("video.mp4", "rb") as f:
                await update.message.reply_video(f)

            os.remove("video.mp4")

            await msg.delete()

        else:
            await msg.edit_text("❌ فشل تحميل الفيديو")

    except Exception as e:
        await msg.edit_text(f"❌ خطأ:\n{e}")

    downloading = False


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("TikTok Bot Running")

app.run_polling()
