import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso'

# إعدادات قوية جداً لجلب الفيديو مع الصوت والصور واليوتيوب
YDL_OPTS = {
    # 'best' تضمن جلب فيديو كامل (صوت وصورة) في ملف واحد لتجنب مشكلة الصمت
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    # ضروري لتحويل سلايد الصور في تيك توك إلى فيديو
    'allow_unplayable_formats': True,
    'merge_output_format': 'mp4',
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت جاهز تماماً! أرسل رابط (يوتيوب، تيك توك فيديو أو صور، انستقرام) وسأحمله لك فوراً.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري التحميل والمعالجة (قد يستغرق اليوتيوب وقتاً أطول قليلاً)...")

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # تنظيف الروابط لضمان عدم حدوث خطأ Unsupported URL
            clean_url = url.split('?')[0] if "tiktok" in url else url
            info = ydl.extract_info(clean_url, download=True)
            file_path = ydl.prepare_filename(info)

        # زر المطور فقط لقناتك
        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # إرسال الفيديو (شامل الصوت والصور المحولة)
        with open(file_path, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption="✅ تم التحميل بنجاح",
                reply_markup=reply_markup,
                supports_streaming=True
            )

        await status_msg.delete()

    except Exception as e:
        # رسالة الخطأ التي ظهرت في صورك
        await update.message.reply_text("❌ عذراً، هذا الرابط محمي أو يحتاج تحديث للمكتبة.")
        print(f"Error: {e}")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        # --- تنظيف الذاكرة فوراً لضمان عدم عطل البوت في Railway ---
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()
