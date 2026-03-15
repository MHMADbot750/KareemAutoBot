import os
import asyncio
import subprocess
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [الإعدادات] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso'

def update_engine():
    try:
        subprocess.check_call(["pip", "install", "--upgrade", "yt-dlp"])
    except: pass

update_engine()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🜄🜏 جاهز للعمل سيدي المطور 🔥\n• يوتيوب ⮕ فيديو\n• تيك توك ⮕ صوت فقط")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⚡ جاري تحليل الرابط واستخراج البيانات...")

    # تحديد نوع الملف بناءً على الرابط
    is_tiktok = "tiktok.com" in url
    
    # إعدادات مخصصة لكل موقع لضمان كسر الحماية
    ydl_opts = {
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        }
    }

    if is_tiktok:
        # إعدادات التيك توك: صوت فقط بأعلى جودة
        ydl_opts['format'] = 'bestaudio/best'
    else:
        # إعدادات اليوتيوب: فيديو MP4 جاهز (تجاوز FFmpeg)
        ydl_opts['format'] = 'best[ext=mp4]/best'
        ydl_opts['extractor_args'] = {'youtube': {'player_client': ['ios']}}

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if is_tiktok:
            # إرسال الصوت للتيك توك
            with open(file_path, 'rb') as audio:
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=audio,
                    caption="✅ تم استخراج صوت تيك توك بنجاح",
                    reply_markup=reply_markup
                )
        else:
            # إرسال الفيديو لليوتيوب
            with open(file_path, 'rb') as video:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=video,
                    caption="✅ تم تحميل فيديو يوتيوب بنجاح",
                    reply_markup=reply_markup,
                    supports_streaming=True
                )

        await status_msg.delete()

    except Exception as e:
        update_engine()
        await update.message.reply_text("⚠️ فشل التجاوز. تم تحديث النظام تلقائياً، حاول مرة أخرى.")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        await asyncio.sleep(2)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                # حذف بقايا الملفات المؤقتة
                base = os.path.splitext(file_path)[0]
                for ext in ['.part', '.ytdl', '.mp4', '.m4a', '.mp3']:
                    if os.path.exists(base + ext): os.remove(base + ext)
            except: pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    app.run_polling()

if __name__ == '__main__':
    main()
