import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [الإعدادات الأساسية] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso'

# إعدادات متقدمة لتجاوز حظر العمر وحماية اليوتيوب
YDL_OPTS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    # إضافة هوية متصفح قوية وتجاوز قيود العمر
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'referer': 'https://www.youtube.com/',
    'age_limit': 100, # محاولة تجاوز قيود العمر برمجياً
    'merge_output_format': 'mp4',
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ نظام المختبر السري جاهز. أرسل رابط اليوتيوب المحمي وسأحاول اختراقه.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري تجاوز حماية يوتيوب ومعالجة الفيديو...")

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # التأكد من وجود الملف قبل الإرسال لتجنب خطأ Errno 2
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as video:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=video,
                    caption="✅ تم التجاوز والتحميل بنجاح",
                    reply_markup=reply_markup,
                    read_timeout=100,
                    write_timeout=100
                )
        else:
            raise Exception("الملف غير موجود بعد التحميل")

        await status_msg.delete()

    except Exception as e:
        error_text = str(e)
        if "Sign in to confirm your age" in error_text:
            await update.message.reply_text("❌ هذا الفيديو يتطلب تسجيل دخول (قيود عمرية). سأحتاج لملف cookies.txt لتجاوزه.")
        else:
            await update.message.reply_text(f"❌ خطأ في النظام: {error_text[:60]}")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        # تأخير الحذف ثواني بسيطة للتأكد من اكتمال الإرسال لتجنب خطأ No such file
        await asyncio.sleep(5) 
        if file_path and os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    app.run_polling()

if __name__ == '__main__':
    main()
