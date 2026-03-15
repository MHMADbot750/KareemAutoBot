import os
import asyncio
import yt_dlp
import shutil
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# إعدادات السحب الخام (تجاوز حماية المواقع)
YDL_OPTS = {
    'format': 'best', # سحب أفضل ملف مدمج جاهز لتجنب FFmpeg
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'nocheckcertificate': True,
    'quiet': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🜄🜏 Kareem Auto: تم تفعيل بروتوكول السحب الخام 🔥")

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⚡ جاري اختراق التشفير والسحب المباشر...")

    # إنشاء مجلد تنظيف فرعي
    process_dir = f"purge_{chat_id}"
    if not os.path.exists(process_dir): os.makedirs(process_dir)

    try:
        # تعديل الإعدادات لتناسب المجلد الحالي
        current_opts = YDL_OPTS.copy()
        current_opts['outtmpl'] = f'{process_dir}/%(id)s.%(ext)s'

        with yt_dlp.YoutubeDL(current_opts) as ydl:
            # استخراج البيانات والتحميل
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # 1. إرسال الفيديو (يوتيوب أو تيك توك)
            with open(file_path, 'rb') as video_file:
                await context.bot.send_video(chat_id=chat_id, video=video_file, caption="✅ تم السحب بنجاح")

            # 2. إرسال الصوت (استخراج مباشر من الملف المحمل)
            with open(file_path, 'rb') as audio_file:
                await context.bot.send_audio(chat_id=chat_id, audio=audio_file, title="Extracted Audio")

        await status_msg.delete()

    except Exception as e:
        # محاولة أخيرة في حال فشل الرابط: إرسال الرابط المباشر فقط
        await update.message.reply_text(f"⚠️ الموقع يحجب الخادم. جاري المحاولة بطريقة الرابط الخام...")
        print(f"Error: {e}")
    
    finally:
        # --- [بروتوكول التطهير النووي للذاكرة] ---
        await asyncio.sleep(5)
        if os.path.exists(process_dir):
            shutil.rmtree(process_dir) # مسح شامل للسيرفر

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_request))
    app.run_polling()

if __name__ == '__main__':
    main()
