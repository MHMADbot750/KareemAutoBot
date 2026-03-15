import os
import asyncio
import yt_dlp
import shutil
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [الإعدادات الأساسية] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# إعدادات الاستخراج القصوى (تجاوز الحماية + أعلى جودة)
YDL_OPTS = {
    'format': 'bestvideo+bestaudio/best',
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
    await update.message.reply_text("🜄🜏 تم تفعيل نظام Kareem Auto الشامل 🔥\n(فيديو + صور + استخراج الصوت + تنظيف تلقائي للذاكرة)")

async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if "tiktok.com" not in url: return

    status_msg = await update.message.reply_text("⚡ جاري المعالجة والاستخراج...")

    # إنشاء مجلد مؤقت فرعي لكل عملية لضمان التنظيف الشامل
    process_dir = f"temp_{chat_id}_{asyncio.get_event_loop().time()}"
    if not os.path.exists(process_dir): os.makedirs(process_dir)

    try:
        current_opts = YDL_OPTS.copy()
        current_opts['outtmpl'] = f'{process_dir}/%(id)s.%(ext)s'

        with yt_dlp.YoutubeDL(current_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # --- [المرحلة 1: إرسال المحتوى (فيديو أو صور)] ---
            if info.get('formats') is None or 'entries' in info:
                # معالجة نظام الصور (Slideshow)
                images = [f.get('url') for f in info.get('requested_formats', []) if 'url' in f] or [info.get('url')]
                media_group = [InputMediaPhoto(img) for img in images[:10]]
                if media_group:
                    await context.bot.send_media_group(chat_id=chat_id, media=media_group)
            else:
                # معالجة الفيديو العادي
                file_path = ydl.prepare_filename(info)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as v:
                        await context.bot.send_video(chat_id=chat_id, video=v, caption="✅ تم تحميل الفيديو")

            # --- [المرحلة 2: استخراج وإرسال الصوت] ---
            # نستخدم الرابط المباشر للصوت لسرعة الاستجابة وتوفير الذاكرة
            audio_url = info.get('url')
            await context.bot.send_audio(
                chat_id=chat_id, 
                audio=audio_url, 
                title="TikTok Audio Trace", 
                performer="Kareem Auto Bot"
            )

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"⚠️ فشل النظام: {str(e)[:50]}")
    
    finally:
        # --- [المرحلة 3: تنظيف الذاكرة مباشرة] ---
        # الانتظار لضمان اكتمال الإرسال قبل المسح
        await asyncio.sleep(5)
        if os.path.exists(process_dir):
            shutil.rmtree(process_dir) # مسح المجلد بالكامل من السيرفر فوراً

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok))
    app.run_polling()

if __name__ == '__main__':
    main()
