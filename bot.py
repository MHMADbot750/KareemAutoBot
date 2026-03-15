import os
import asyncio
import yt_dlp
import shutil
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [ الإعدادات ] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# إعدادات تجعل السيرفر يظهر كأنه متصفح حقيقي لتجنب الحظر
YDL_OPTS = {
    'format': 'best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك في Kareem Auto 🚀\nأرسل رابط فيديو أو صور من تيك توك وسأقوم بالتحميل فوراً.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري التحميل ومعالجة الملفات...")

    # إنشاء مجلد مؤقت خاص بهذه العملية فقط لسهولة الحذف
    temp_folder = f"work_{chat_id}_{int(asyncio.get_event_loop().time())}"
    if not os.path.exists(temp_folder): os.makedirs(temp_folder)

    try:
        current_opts = YDL_OPTS.copy()
        current_opts['outtmpl'] = f'{temp_folder}/%(id)s.%(ext)s'

        with yt_dlp.YoutubeDL(current_opts) as ydl:
            # استخراج البيانات وتحميل الملف
            info = ydl.extract_info(url, download=True)
            
            # 1. إذا كان المحتوى ألبوم صور (Slideshow)
            if 'entries' in info or (not info.get('url') and info.get('formats') is None):
                images = info.get('requested_formats', []) or info.get('entries', [])
                img_urls = [i.get('url') for i in images if i.get('url')]
                if img_urls:
                    media = [InputMediaPhoto(u) for u in img_urls[:10]]
                    await context.bot.send_media_group(chat_id=chat_id, media=media)
            
            # 2. إذا كان فيديو عادي (من تيك توك أو يوتيوب أو غيره)
            file_path = ydl.prepare_filename(info)
            if os.path.exists(file_path):
                # إرسال الفيديو
                with open(file_path, 'rb') as v:
                    await context.bot.send_video(chat_id=chat_id, video=v, caption="✅ تم تحميل الفيديو")
                
                # إرسال الصوت بشكل مستقل تحت الفيديو
                with open(file_path, 'rb') as a:
                    await context.bot.send_audio(chat_id=chat_id, audio=a, title="الصوت المستخرج")

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text("⚠️ عذراً، لم أتمكن من جلب البيانات. تأكد من الرابط أو حاول مرة أخرى.")
        print(f"Error: {e}")
    
    finally:
        # --- [ بروتوكول تنظيف الخادم فوري ] ---
        # ننتظر 5 ثوانٍ لضمان اكتمال الرفع للتلجرام ثم نمسح كل شيء
        await asyncio.sleep(5)
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder) # حذف المجلد والملفات تماماً من ذاكرة السيرفر

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    app.run_polling()

if __name__ == '__main__':
    main()
