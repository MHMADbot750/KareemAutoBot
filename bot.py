import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso'

# إعدادات معززة لتجاوز قيود الحماية ودعم كافة الصيغ
YDL_OPTS = {
    # دمج الصوت والصورة بأعلى جودة ممكنة تلقائياً
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    # هويّة متصفح حديثة جداً لتجنب كشف "البوت" من قبل تيك توك ويوتيوب
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'referer': 'https://www.tiktok.com/',
    # تفعيل خيارات تحويل الصور (Slide Show) إلى فيديو MP4
    'allow_unplayable_formats': True,
    'merge_output_format': 'mp4',
    'extract_flat': False,
    'wait_for_video': True,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ نظام التحميل في المختبر السري يعمل. أرسل الرابط للمعالجة.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري سحب البيانات وتجاوز الحماية...")

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # تنظيف الرابط لضمان عدم رفض الطلب من السيرفر
            clean_url = url.split('?')[0] if "tiktok" in url else url
            info = ydl.extract_info(clean_url, download=True)
            if not info:
                raise Exception("فشل جلب البيانات")
            
            file_path = ydl.prepare_filename(info)

        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # التأكد من وجود الملف قبل محاولة الإرسال
        if os.path.exists(file_path):
            # إرسال الفيديو (شامل الصوت والصور المحولة)
            with open(file_path, 'rb') as video:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=video,
                    caption="✅ تم استخراج البيانات بنجاح",
                    reply_markup=reply_markup,
                    supports_streaming=True
                )
            
            # إرسال الصوت بشكل منفصل (اختياري، تم إبقاؤه لضمان شمولية الاستخراج)
            with open(file_path, 'rb') as audio:
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=audio,
                    title="Audio Extraction",
                    performer="Kareem Auto Bot"
                )

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text("❌ خطأ أمني: فشل تجاوز حماية الرابط. تأكد من تحديث المكتبة أو استخدام بروكبسي.")
        print(f"Detailed Lab Error: {e}")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        # بروتوكول مسح الأثر: تنظيف الذاكرة فوراً
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    app.run_polling()

if __name__ == '__main__':
    main()
