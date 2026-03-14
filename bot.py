import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# إعدادات بسيطة لضمان التحميل السريع
YDL_OPTS = {
    'format': 'best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت جاهز! أرسل الرابط الآن.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        return

    # إرسال رسالة "جاري التحميل" بدلاً من ملصق مؤقتاً للتأكد من العمل
    prog_msg = await update.message.reply_text("⏳ جاري المعالجة والتحميل...")

    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # أزرار شفافة
        keyboard = [[InlineKeyboardButton("المطور", url="https://t.me/your_user")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # إرسال الفيديو
        with open(file_path, 'rb') as video:
            await context.bot.send_video(chat_id=update.message.chat_id, video=video, caption="✅ تم بنجاح", reply_markup=reply_markup)

        # إرسال الصوت
        with open(file_path, 'rb') as audio:
            await context.bot.send_audio(chat_id=update.message.chat_id, audio=audio, title="Audio")

        await prog_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
    
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
