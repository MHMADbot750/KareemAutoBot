import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url: return

    msg = await update.message.reply_text("⏳ جاري التحميل... قد يستغرق الأمر دقيقة")
    chat_id = update.message.chat_id
    video_file = f"video_{chat_id}.mp4"
    audio_file = f"audio_{chat_id}.mp3"
    
    try:
        # تحميل الفيديو أولاً
        ydl_opts_v = {'format': 'best', 'outtmpl': video_file, 'quiet': True}
        if "youtube" in url or "youtu.be" in url: ydl_opts_v['cookiefile'] = 'youtube.com_cookies.txt'
        
        with yt_dlp.YoutubeDL(ydl_opts_v) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        
        await update.message.reply_video(video=open(video_file, 'rb'), caption="🎬 تم تحميل الفيديو")

        # محاولة استخراج الصوت (إذا فشل لن يتوقف البوت)
        try:
            ydl_opts_a = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio_temp',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
                'quiet': True
            }
            if "youtube" in url or "youtu.be" in url: ydl_opts_a['cookiefile'] = 'youtube.com_cookies.txt'
            
            with yt_dlp.YoutubeDL(ydl_opts_a) as ydl:
                await asyncio.to_thread(ydl.download, [url])
            
            if os.path.exists('audio_temp.mp3'):
                await update.message.reply_audio(audio=open('audio_temp.mp3', 'rb'), caption="🎵 تم استخراج الصوت")
                os.remove('audio_temp.mp3')
        except:
            await update.message.reply_text("⚠️ الفيديو وصل، لكن استخراج الصوت فشل (تحتاج إضافة ffmpeg لـ Railway)")

        await msg.delete()
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")
    finally:
        if os.path.exists(video_file): os.remove(video_file)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    application.run_polling()

if __name__ == '__main__':
    main()
