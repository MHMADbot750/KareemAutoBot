import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
CHANNEL_URL = 'https://t.me/ll3lso' # رابط قناتك

# إعدادات التحميل الشاملة لضمان الجودة
YDL_OPTS = {
    'format': 'best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ أهلاً بك! أرسل رابط تيك توك أو انستقرام وسأقوم بالتحميل فوراً.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not url.startswith("http"):
        return

    # 1. إرسال رسالة "جاري التحميل" (يمكنك تغييرها لملصق إذا أردت)
    status_msg = await update.message.reply_text("⏳ جاري التحميل... انتظر قليلاً")

    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # 2. إعداد الأزرار الشفافة كما في الصورة المطلوبة
        keyboard = [
            [InlineKeyboardButton("🎵 FindMusic Spotify", url="https://t.me/FindMusicSpotify")],
            [InlineKeyboardButton("🛑 YouTube download bot", url="https://t.me/YoutubeDownloadBot")],
            [InlineKeyboardButton("👨‍💻 المطور", url=CHANNEL_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # 3. إرسال الفيديو أولاً مع الأزرار
        with open(file_path, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption="✅ تم التحميل بنجاح",
                reply_markup=reply_markup
            )

        # 4. إرسال الصوت أسفل الفيديو مباشرة
        with open(file_path, 'rb') as audio:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio,
                title="الصوت المستخرج",
                performer="Kareem Auto Bot",
                caption="🎵 ملف الصوت"
            )

        # حذف رسالة الانتظار
        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        # 5. الحذف التلقائي لتنظيف خادم Railway فوراً
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    
    print("البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == '__main__':
    main()
