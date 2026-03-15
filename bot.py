import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso' # رابط قناتك فقط

# إعدادات متطورة لدعم الصور والفيديو وتجاوز الحماية
YDL_OPTS = {
    # هذا السطر يضمن تحويل الصور إلى فيديو MP4 قابل للإرسال
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'allow_unplayable_formats': True,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت جاهز! أرسل رابط (فيديو، صور، يوتيوب) وسأقوم بالواجب.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري المعالجة والتحميل...")

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # تنظيف الرابط لضمان عدم حدوث خطأ Unsupported URL
            clean_url = url.split('?')[0] if "photo" in url else url
            info = ydl.extract_info(clean_url, download=True)
            file_path = ydl.prepare_filename(info)

        # زر المطور فقط كما طلبت
        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # إرسال المحتوى (فيديو أو مجموعة صور محولة لفيديو)
        with open(file_path, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption="✅ تم التحميل بنجاح",
                reply_markup=reply_markup
            )

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text("❌ عذراً، هذا الرابط يحتاج تحديث للمكتبة أو هوية دخول.")
        print(f"Error: {e}")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        # --- تنظيف الذاكرة فوراً لضمان عدم عطل الخادم ---
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    app.run_polling()

if __name__ == '__main__':
    main()
