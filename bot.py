import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# التوكن الخاص بك
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# إعدادات التحميل الاحترافية
YDL_OPTS = {
    'format': 'best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت جاهز! أرسل أي رابط (تيك توك، انستقرام) وسأقوم بالواجب.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    # 1. إرسال ملصق الانتظار (استخدم ايدي ملصق متحرك)
    wait_msg = await update.message.reply_sticker("CAACAgIAAxkBAAEL...") 

    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # 2. إعداد الأزرار الشفافة كما في الصورة
        keyboard = [
            [InlineKeyboardButton("🎵 FindMusic Spotify", url="https://t.me/your_bot")],
            [InlineKeyboardButton("🛑 YouTube download bot", url="https://t.me/your_bot")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # 3. إرسال الفيديو
        with open(file_path, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption="✅ تم التحميل بنجاح",
                reply_markup=reply_markup
            )

        # 4. إرسال الصوت (كفيديو صوتي تحت الأصلي)
        with open(file_path, 'rb') as audio:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio,
                title="الصوت المستخرج",
                performer="البوت الخاص بك"
            )

        # حذف ملصق الانتظار بعد النجاح
        await wait_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ فني: {str(e)}")
        if wait_msg: await wait_msg.delete()
    
    finally:
        # 5. تنظيف الخادم فوراً للحفاظ على موارد Railway
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    print("البوت قيد التشغيل...")
    app.run_polling()

if __name__ == '__main__':
    main()
