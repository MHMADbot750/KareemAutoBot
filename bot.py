import os
import asyncio
import yt_dlp
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# توكن البوت الخاص بك من BotFather
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# إعدادات yt-dlp للتحميل الشامل (تيك توك، انستقرام، يوتيوب... إلخ)
YDL_OPTIONS = {
    'format': 'best',
    'outtmpl': 'downloads/%(id)s.%(ext)s', # حفظ في مجلد مؤقت
    'noplaylist': True,
    'restrictfilenames': True,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل لي رابط فيديو من تيك توك أو انستقرام وسأقوم بتحميله لك فوراً.")

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id

    # 1. إرسال ملصق متحرك (استبدل المعرف بملصق من اختيارك)
    # ملاحظة: يمكنك الحصول على معرف الملصق عن طريق إرساله لبوت @idstickerbot
    status_msg = await update.message.reply_sticker("CAACAgIAAxkBAAEJ...") 

    try:
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            audio_path = video_path.rsplit('.', 1)[0] + ".mp3"

        # 2. إرسال الفيديو
        with open(video_path, 'rb') as video:
            sent_video = await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption="✅ تم التحميل بنجاح عبر بوتك"
            )

        # 3. استخراج وإرسال الصوت (اختياري كما في الصورة)
        # ملاحظة: yt-dlp يحمل الفيديو، سنرسله كملف صوتي أيضاً
        with open(video_path, 'rb') as audio:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio,
                title="الصوت المستخرج",
                performer="المؤدي غير معروف"
            )

        # 4. حذف الملصق بعد الانتهاء
        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء المعالجة: {str(e)}")
    
    finally:
        # 5. الحذف التلقائي من الخادم (Railway) لتنظيف الذاكرة
        if 'video_path' in locals() and os.path.exists(video_path):
            os.remove(video_path)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    
    print("البوت يعمل الآن...")
    application.run_polling()

if __name__ == '__main__':
    main()
