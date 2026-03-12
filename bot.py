import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    msg = await update.message.reply_text("🐿️ جاري التحميل...")

    ydl_opts_list = [

        # الطريقة 1
        {
            "format": "best",
            "outtmpl": "video.%(ext)s",
            "quiet": True,
            "noplaylist": True
        },

        # الطريقة 2 (وضع Android)
        {
            "format": "best",
            "outtmpl": "video.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            }
        },

        # الطريقة 3 (وضع Web)
        {
            "format": "best",
            "outtmpl": "video.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["web"]
                }
            }
        }
    ]

    filename = None

    for opts in ydl_opts_list:
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            break
        except:
            continue

    if filename and os.path.exists(filename):
        await msg.delete()
        with open(filename, "rb") as f:
            await update.message.reply_video(f)
        os.remove(filename)
    else:
        await msg.edit_text("❌ فشل تحميل الفيديو")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot started")
app.run_polling()
