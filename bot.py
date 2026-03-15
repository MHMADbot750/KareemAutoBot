import os
import asyncio
import yt_dlp
import shutil
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [الإعدادات التقنية] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# إعدادات المحرك لضمان التحميل من كافة المواقع وسرعة المعالجة
YDL_OPTS = {
    'format': 'best', 
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🜄🜏 أهلاً بك في بوت Kareem Auto للتحميل 🔥\n1️⃣ أرسل الرابط (تيك توك، يوتيوب، إلخ)\n2️⃣ سأرسل لك الفيديو + الصوت\n3️⃣ يتم تنظيف السيرفر تلقائياً بعد كل عملية")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري التحميل ومعالجة الطلب...")

    # إنشاء مجلد فرعي مؤقت لكل عملية لضمان حذف الملفات بالكامل
    temp_dir = f"worker_{chat_id}_{int(asyncio.get_event_loop().time())}"
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)

    try:
        opts = YDL_OPTS.copy()
        opts['outtmpl'] = f'{temp_dir}/%(id)s.%(ext)s'

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # --- [المرحلة 1: فحص نوع المحتوى (صور أو فيديو)] ---
            if 'entries' in info or (not info.get('url') and info.get('formats') is None):
                # إذا كان الرابط ألبوم صور (Slideshow تيك توك)
                images = info.get('requested_formats', []) or info.get('entries', [])
                img_urls = [img.get('url') for img in images if img.get('url')]
                if img_urls:
                    media_group = [InputMediaPhoto(u) for u in img_urls[:10]]
                    await context.bot.send_media_group(chat_id=chat_id, media=media_group)
            else:
                # إذا كان فيديو عادي (يوتيوب أو تيك توك)
                file_path = ydl.prepare_filename(info)
                if os.path.exists(file_path):
                    # إرسال الفيديو أولاً
                    with open(file_path, 'rb') as v:
                        await context.bot.send_video(chat_id=chat_id, video=v, caption="✅ تم تحميل الفيديو بنجاح")
                    
                    # إرسال الصوت تحت الفيديو مباشرة
                    with open(file_path, 'rb') as a:
                        await context.bot.send_audio(chat_id=chat_id, audio=a, title="الصوت المستخرج", performer="Kareem Auto")

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"⚠️ عذراً، تعذر التحميل. تأكد من الرابط أو حاول لاحقاً.")
        print(f"Error: {e}")
    
    finally:
        # --- [المرحلة 2: تفريغ الذاكرة وحذف الملفات فوراً] ---
        # الانتظار لثوانٍ قليلة لضمان انتهاء الرفع للتلجرام
        await asyncio.sleep(5)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir) # حذف المجلد ومحتوياته من السيرفر نهائياً

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    app.run_polling()

if __name__ == '__main__':
    main()
