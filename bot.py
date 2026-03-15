import os
import asyncio
import subprocess
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [Operational Config] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso'

def update_system():
    """تحديث المحرك لكسر حمايات 2026 الجديدة"""
    try:
        subprocess.check_call(["pip", "install", "--upgrade", "yt-dlp"])
    except: pass

# تحديث عند الإقلاع
update_system()

# إعدادات الاستخراج (ناريّة - شاملة - بدون FFmpeg)
YDL_OPTS = {
    'format': 'best[ext=mp4]/best', # ضمان جودة MP4 مدمجة الصوت
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'extractor_args': {'youtube': {'player_client': ['ios']}}, # انتحال هوية آيفون
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        'Accept': '*/*',
        'Referer': 'https://www.google.com/',
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🜄🜏 البوت الناري جاهز سيدي المطور 🔥\nأرسل أي رابط (يوتيوب، تيك توك، إلخ) وسأستخرج لك الفيديو والصوت فوراً.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if not url.startswith("http"): return

    prog_msg = await update.message.reply_text("⚡ جاري استخراج البيانات وكسر التشفير...")

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # 1. إرسال الفيديو (المهمة الأولى)
        with open(file_path, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption="✅ تم تحميل الفيديو بنجاح",
                reply_markup=reply_markup,
                supports_streaming=True
            )
        
        # 2. إرسال الصوت (المهمة الثانية - تحت الفيديو مباشرة)
        with open(file_path, 'rb') as audio:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio,
                title="Audio Extraction",
                performer="Kareem Auto Bot"
            )

        await prog_msg.delete()

    except Exception as e:
        update_system() # تحديث النظام عند الفشل
        await update.message.reply_text("⚠️ الموقع قام بتغيير التشفير. تم تحديث أسلحتنا، أعد إرسال الرابط.")
        if 'prog_msg' in locals(): await prog_msg.delete()
    
    finally:
        # تطهير الخادم (مسح الأثر)
        await asyncio.sleep(3)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                base = os.path.splitext(file_path)[0]
                for ext in ['.part', '.ytdl', '.mp4']:
                    if os.path.exists(base + ext): os.remove(base + ext)
            except: pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    print("🔱 LØGHØST-Z Core is Active...")
    app.run_polling()

if __name__ == '__main__':
    main()
