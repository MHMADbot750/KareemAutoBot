import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso' # رابط قناتك فقط

# إعدادات متطورة لتجاوز الحماية وتنظيف الذاكرة تلقائياً
YDL_OPTS = {
    'format': 'best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ أهلاً بك! أرسل رابط تيك توك أو انستقرام للتحميل فوراً.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري المعالجة والتحميل...")

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # تنظيف الرابط من التتبع لحل مشكلة Unsupported URL
            clean_url = url.split('?')[0]
            info = ydl.extract_info(clean_url, download=True)
            if not info:
                info = ydl.extract_info(url, download=True)
            
            file_path = ydl.prepare_filename(info)

        # زر المطور فقط كما طلبت
        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # إرسال الفيديو
        with open(file_path, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption="✅ تم التحميل بنجاح",
                reply_markup=reply_markup
            )

        # إرسال الصوت أسفل الفيديو
        with open(file_path, 'rb') as audio:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio,
                title="الصوت المستخرج",
                performer="Kareem Auto Bot",
                caption="🎵 ملف الصوت"
            )

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text("❌ عذراً، حدث خطأ في معالجة هذا الرابط. تأكد من تحديث المكتبة.")
        print(f"Error: {e}")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        # --- تنظيف ذاكرة الخادم فوراً ---
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()
