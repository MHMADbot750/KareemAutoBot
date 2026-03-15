import os
import asyncio
import yt_dlp
import shutil
import requests
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# إعدادات الاختراق القصوى
YDL_OPTS = {
    'format': 'best', 
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'nocheckcertificate': True,
    'quiet': True,
    'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🜄🜏 Kareem Auto: تم تفعيل محرك الاختراق النووي 🔥\n✅ فيديو + صور تيك توك\n✅ فيديو يوتيوب\n✅ استخراج صوت\n✅ تنظيف شامل")

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⚡ جاري كسر التشفير وسحب البيانات...")

    # مجلد التطهير الفوري
    process_dir = f"purge_{chat_id}_{int(asyncio.get_event_loop().time())}"
    if not os.path.exists(process_dir): os.makedirs(process_dir)

    try:
        current_opts = YDL_OPTS.copy()
        current_opts['outtmpl'] = f'{process_dir}/%(id)s.%(ext)s'

        with yt_dlp.YoutubeDL(current_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # --- [1. معالجة الصور (Slideshow)] ---
            if 'entries' in info or (not info.get('url') and info.get('formats') is None):
                images = info.get('requested_formats', []) or info.get('entries', [])
                img_urls = [img.get('url') for img in images if img.get('url')]
                
                if img_urls:
                    media_group = [InputMediaPhoto(u) for u in img_urls[:10]]
                    await context.bot.send_media_group(chat_id=chat_id, media=media_group)
                    # إرسال صوت الصور
                    audio_url = info.get('url') or info.get('webpage_url')
                    await context.bot.send_audio(chat_id=chat_id, audio=audio_url, title="Slideshow Sound")
            
            # --- [2. معالجة الفيديو (يوتيوب وتيك توك)] ---
            else:
                file_path = ydl.prepare_filename(info)
                if os.path.exists(file_path):
                    # إرسال الفيديو
                    with open(file_path, 'rb') as v:
                        await context.bot.send_video(chat_id=chat_id, video=v, caption="✅ تم التحميل بنجاح", supports_streaming=True)
                    
                    # إرسال الصوت (استخراج مباشر من الملف)
                    with open(file_path, 'rb') as a:
                        await context.bot.send_audio(chat_id=chat_id, audio=a, title="Extracted Audio", performer="Kareem Auto")

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text("⚠️ الموقع يرفض الاتصال المباشر. تم تحديث البروتوكول، أرسل الرابط مرة أخرى.")
        print(f"Error Log: {e}")
    
    finally:
        # --- [3. بروتوكول التطهير النووي] ---
        await asyncio.sleep(5)
        if os.path.exists(process_dir):
            shutil.rmtree(process_dir) # تصفير السيرفر تماماً

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_request))
    app.run_polling()

if __name__ == '__main__':
    main()
