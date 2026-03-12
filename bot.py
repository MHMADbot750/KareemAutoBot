import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtu" not in url:
        await update.message.reply_text("❌ أرسل رابط يوتيوب فقط")
        return

    msg = await update.message.reply_text("⏳ جاري جلب الفيديو...")

    try:
        api = f"https://p.oceansaver.in/ajax/download.php?format=720&url={url}"
        data = requests.get(api).json()

        video = data["url"]

        await msg.delete()
        await update.message.reply_video(video)

    except Exception as e:
        await msg.edit_text("❌ فشل تحميل الفيديو")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot started")
app.run_polling()
