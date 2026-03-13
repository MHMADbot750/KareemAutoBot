import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# التوكن الخاص بك
TOKEN = "8701664697:AAEuxlF3u933O6-7D_p8G0N-X0YpL2mI"

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    # التأكد من أن الرسالة رابط
    if not (url.startswith("http://") or url.startswith("https://")):
        return

    msg = await update.message.reply_text("⏳ Processing your video... please wait")
    
    # إعدادات التحميل
    ydl_opts = {
        'format': 'best',
        'cookiefile': 'youtube.com_cookies.txt', 
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        # تنفيذ التحميل
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # إرسال الفيديو للمستخدم
        with open('video.mp4', 'rb') as video_file:
            await update.message.reply_video(video=video_file)
        
        # تنظيف الملفات المؤقتة
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')
            
        await msg.delete()
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    # بناء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # التعامل مع الرسائل النصية
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    # بدء تشغيل البوت
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
