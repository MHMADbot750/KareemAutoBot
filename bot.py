import os
import asyncio
import yt_dlp
import shutil
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [Operational Config] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

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
    await update.message.reply_text("🜄🜏 تم تفعيل نظام KareemAuto الشامل 🔥\nدعم كامل لـ: (فيديو تيك توك - صور تيك توك - استخراج الصوت)")

async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if "tiktok.com" not in url: return

    status_msg = await update.message.reply_text("⚡ جاري استخراج المحتوى (فيديو/صور) وتطهير النظام...")

    # إنشاء مجلد فرعي لكل عملية لضمان عدم تداخل الملفات وتسهيل التطهير
    download_dir = f"downloads_{chat_id}"
    if not os.path.exists(download_dir): os.makedirs(download_dir)

    try:
        current_opts = YDL_OPTS.copy()
        current_opts['outtmpl'] = f'{download_dir}/%(id)s.%(ext)s'

        with yt_dlp.YoutubeDL(current_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # التحقق إذا كان الرابط يحتوي على صور (Slideshow)
            if 'entries' in info or info.get('formats') is None:
                # منطق معالجة الصور
                images = [f.get('url') for f in info.get('requested_formats', []) if 'url' in f] or [info.get('url')]
                media_group = [InputMediaPhoto(img) for img in images[:10]] # بحد أقصى 10 صور للتلجرام
                
                if media_group:
                    await context.bot.send_media_group(chat_id=chat_id, media=media_group)
                    # إرسال الصوت الخاص بالصور
                    audio_url = info.get('url') # غالباً ما يكون الرابط نفسه يحتوي على الصوت
                    await update.message.reply_audio(audio=audio_url, title="TikTok Slideshow Audio")
            else:
                # منطق معالجة الفيديو العادي
                file_path = ydl.prepare_filename(info)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as v:
                        await context.bot.send_video(chat_id=chat_id, video=v, caption="✅ فيديو تيك توك")
                    with open(file_path, 'rb') as a:
                        await context.bot.send_audio(chat_id=chat_id, audio=a, title="TikTok Audio")

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"⚠️ فشل في النظام: {str(e)[:50]}")
    
    finally:
        # --- [بروتوكول التطهير النووي] ---
        await asyncio.sleep(5)
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir) # حذف المجلد بالكامل مع كل ما بداخله

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok))
    app.run_polling()

if __name__ == '__main__':
    main()
