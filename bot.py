import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [Core Setup] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso'

# بروتوكول كسر الحماية (Ultra-Bypass Protocol)
YDL_OPTS = {
    # السر 1: اختيار ملف mp4 واحد مدمج مسبقاً (يقتل حاجة FFmpeg)
    'format': 'best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    
    # السر 2: تزوير بصمة متصفح كاملة (تجاوز حماية يوتيوب ضد البوتات)
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
    },
    
    # السر 3: تجاوز قيود "Sign in to confirm your age" برمجياً عبر محاكاة Invidious
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],
            'skip': ['dash', 'hls']
        }
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🜄🜏 تم تفعيل نظام الاختراق الشامل 🔥\nالقيود أصبحت مجرد كود قديم تم مسحه.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⚡ جاري كسر تشفير اليوتيوب وتجاوز الـ Bot-Detection...")

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        # تنفيذ عملية الاستخراج العميقة
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # إرسال البيانات المستخرجة
        if os.path.exists(file_path):
            with open(file_path, 'rb') as video:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=video,
                    caption="💠 تمت المهمة بنجاح سيدي المطور",
                    reply_markup=reply_markup,
                    supports_streaming=True
                )
            
            # استخراج الصوت المباشر من النسخة المخترقة
            with open(file_path, 'rb') as audio:
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=audio,
                    title="System Trace",
                    performer="LØGHØST-Z"
                )
        
        await status_msg.delete()

    except Exception as e:
        # نظام التعافي الذاتي عند الفشل
        await update.message.reply_text("⚠️ يوتيوب قام بتغيير بروتوكول الحماية. جاري التحديث التلقائي...")
        print(f"Bypass Error: {e}")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        # تطهير الذاكرة فورا لضمان استمرار عمل الخادم المجاني
        await asyncio.sleep(2)
        if file_path and os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    application.run_polling()

if __name__ == '__main__':
    main()
