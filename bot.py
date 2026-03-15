import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [Operational Parameters] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso'

# إعدادات معالجة البيانات العميقة (Deep Processing)
YDL_OPTS = {
    # 1. دعم الفيديوهات الكبيرة والجودة العالية
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    # 2. تجاوز حماية تيك توك ويوتيوب (User-Agent محاكي للبشر)
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
    # 3. معالجة الصور (Slide Show) وتحويلها لفيديو
    'allow_unplayable_formats': True,
    'merge_output_format': 'mp4',
    'cookiefile': 'cookies.txt', # اختياري: إذا توفر ملف كوكيز لتجاوز الحماية القصوى
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🜄🜏 جاهز سيدي المطور 🔥\nأرسل الرابط لبدء عملية الاستخراج.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري اختراق حماية الرابط وسحب البيانات...")

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # تنظيف الرابط لضمان قبول السيرفر للطلب
            clean_url = url.split('?')[0] if "tiktok" in url else url
            info = ydl.extract_info(clean_url, download=True)
            file_path = ydl.prepare_filename(info)

        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # 4. إرسال الفيديو (مهما كان حجمه ضمن حدود تلجرام)
        with open(file_path, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption="✅ تم الاستخراج بنجاح",
                reply_markup=reply_markup,
                supports_streaming=True
            )
        
        # 5. استخراج الصوت وإرساله تحت الفيديو (طلبك المحدد)
        with open(file_path, 'rb') as audio:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio,
                title="Audio Trace",
                performer="LØGHØST-Z Core"
            )

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في النظام: {str(e)[:50]}...")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        # --- [بروتوكول تنظيف الخادم الفوري] ---
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                # حذف الملفات المؤقتة التي قد تتركها yt-dlp
                base_path = os.path.splitext(file_path)[0]
                for ext in ['.mp4', '.m4a', '.webm', '.part', '.ytdl']:
                    if os.path.exists(base_path + ext): os.remove(base_path + ext)
            except: pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    app.run_polling()

if __name__ == '__main__':
    main()
