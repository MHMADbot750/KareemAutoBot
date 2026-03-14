import os
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# توكن البوت
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل رابط تيك توك أو انستقرام للتحميل.")

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    # 1. إرسال ملصق الانتظار
    status_sticker = await update.message.reply_sticker("CAACAgIAAxkBAAEL...") # ضع ايدي ملصقك هنا

    # إعدادات التحميل (فيديو وصوت)
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'downloads/{chat_id}_%(id)s.%(ext)s',
        'noplaylist': True,
    }

    try:
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            
        # 2. إرسال الفيديو أولاً
        with open(video_path, 'rb') as v_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=v_file,
                caption="تم تحميل الفيديو بنجاح ✅"
            )

        # 3. إرسال نفس الملف كـ "بصمة صوتية" أو ملف صوتي تحت الفيديو مباشرة
        with open(video_path, 'rb') as a_file:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=a_file,
                title="الصوت المستخرج",
                performer="بوتي الخاص",
                caption="تفضل الصوت 🎵"
            )

        # حذف ملصق الانتظار
        await status_sticker.delete()

    except Exception as e:
        await update.message.reply_text(f"❌ فشل التحميل: {str(e)}")
    
    finally:
        # 4. تنظيف الخادم فوراً (مهم جداً لـ Railway)
        if 'video_path' in locals() and os.path.exists(video_path):
            os.remove(video_path)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    print("البوت يعمل بنجاح...")
    app.run_polling()

if __name__ == '__main__':
    main()
