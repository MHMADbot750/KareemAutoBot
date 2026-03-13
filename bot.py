import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# التوكن الجديد الذي أرسلته
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url:
        return

    msg = await update.message.reply_text("⏳ جاري تحميل الفيديو واستخراج الصوت... انتظر قليلاً")
    
    chat_id = update.message.chat_id
    video_file = f"video_{chat_id}.mp4"
    audio_file = f"audio_{chat_id}.mp3"
    
    # إعدادات تحميل الفيديو
    ydl_opts_video = {
        'format': 'best',
        'outtmpl': video_file,
        'quiet': True,
        'no_warnings': True,
    }
    
    # إعدادات استخراج الصوت
    ydl_opts_audio = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio_temp', # ملف مؤقت
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    # استخدام الكوكيز ليوتيوب فقط
    if "youtube" in url or "youtu.be" in url:
        ydl_opts_video['cookiefile'] = 'youtube.com_cookies.txt'
        ydl_opts_audio['cookiefile'] = 'youtube.com_cookies.txt'
    
    try:
        # 1. تحميل الفيديو
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        
        # 2. تحميل واستخراج الصوت
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        
        # البحث عن ملف الصوت الفعلي (لأن yt-dlp يغير الاسم أحياناً)
        actual_audio = 'audio_temp.mp3'
        
        # إرسال الفيديو
        with open(video_file, 'rb') as v:
            await update.message.reply_video(video=v, caption="🎬 تم تحميل الفيديو بنجاح")
            
        # إرسال الصوت
        if os.path.exists(actual_audio):
            with open(actual_audio, 'rb') as a:
                await update.message.reply_audio(audio=a, caption="🎵 تم استخراج الصوت")
            os.remove(actual_audio)
        
        await msg.delete()
        
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
    
    finally:
        # تنظيف الملفات
        if os.path.exists(video_file):
            os.remove(video_file)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    print("البوت يعمل الآن بالتوكن الجديد...")
    application.run_polling()

if __name__ == '__main__':
    main()
