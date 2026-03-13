import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import yt_dlp

# ضع التوكن الخاص ببوتك هنا
BOT_TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="أهلاً بك! أرسل رابط الفيديو لتنزيله.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.effective_chat.id
    
    await context.bot.send_message(chat_id=chat_id, text="جاري المعالجة... قد يستغرق الأمر بعض الوقت.")

    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(id)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # إرسال الفيديو
        await context.bot.send_video(chat_id=chat_id, video=open(filename, 'rb'))
        
        # حذف الملف بعد الإرسال
        os.remove(filename)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"حدث خطأ: {str(e)}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), download_video)
    
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    
    print("البوت يعمل الآن...")
    application.run_polling()
