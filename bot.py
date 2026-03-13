import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933O6-7D_p8G0N-X0YpL2mI"

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url:
        return

    msg = await update.message.reply_text("⏳ جاري جلب الفيديو... انتظر قليلاً")
    
    # اسم الملف المؤقت
    video_file = f"video_{update.message.chat_id}.mp4"
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': video_file,
        'quiet': True,
        'no_warnings': True,
    }

    # إضافة الكوكيز فقط إذا كان الرابط ليوتيوب
    if "youtube" in url or "youtu.be" in url:
        ydl_opts['cookiefile'] = 'youtube.com_cookies.txt'
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        
        await update.message.reply_video(video=open(video_file, 'rb'), caption="تم التحميل بنجاح ✅")
        
        # تنظيف الملفات
        if os.path.exists(video_file):
            os.remove(video_file)
        await msg.delete()
        
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        if os.path.exists(video_file):
            os.remove(video_file)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    application.run_polling()

if __name__ == '__main__':
    main()
