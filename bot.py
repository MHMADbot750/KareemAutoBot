import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso'

# إعدادات متطورة لدعم الصور (Slide Show) واليوتيوب وتجاوز الحماية
YDL_OPTS = {
    # هذا التنسيق يضمن تحميل اليوتيوب بأفضل جودة وصور تيك توك كفيديو
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'allow_unplayable_formats': True,
    'merge_output_format': 'mp4',
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت جاهز! أرسل رابط (يوتيوب، تيك توك فيديو أو صور، انستقرام) وسأقوم بالتحميل.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري التحميل والمعالجة...")

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # تنظيف الرابط لضمان دعم صور تيك توك واليوتيوب
            clean_url = url.split('?')[0] if "tiktok" in url else url
            info = ydl.extract_info(clean_url, download=True)
            file_path = ydl.prepare_filename(info)

        # زر المطور فقط
        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # إرسال الفيديو (سواء كان فيديو أصلي أو صور محولة)
        with open(file_path, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption="✅ تم التحميل بنجاح",
                reply_markup=reply_markup,
                supports_streaming=True
            )

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text("❌ عذراً، هذا الرابط يحتاج تحديث للمكتبة أو هوية دخول.")
        print(f"Error: {e}")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        # --- تنظيف ذاكرة الخادم فوراً لضمان عدم عطل البوت ---
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🧹 تم تنظيف الذاكرة: {file_path}")
            except:
                pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    print("البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == '__main__':
    main()
