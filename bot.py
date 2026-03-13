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
    # ملفات فريدة لكل مستخدم لتجنب التداخل
    video_file = f"video_{chat_id}.mp4"
    audio_file = f"audio_{chat_id}.mp3"
    
    try:
        # 1. تحميل الفيديو بجودة لا تتخطى 720p لتفادي الحجم الكبير
        ydl_opts_v = {
            'format': 'best[height<=720]+bestaudio/best[height<=720]',
            'outtmpl': video_file,
            'quiet': True,
            'merge_output_format': 'mp4'
        }
        
        if "youtube" in url or "youtu.be" in url:
            ydl_opts_v['cookiefile'] = 'youtube.com_cookies.txt'
        
        await asyncio.to_thread(lambda: yt_dlp.YoutubeDL(ydl_opts_v).download([url]))
        
        # إرسال الفيديو
        with open(video_file, 'rb') as v_file:
            await update.message.reply_video(video=v_file, caption="🎬 تم تحميل الفيديو")

        # 2. محاولة استخراج الصوت
        try:
            ydl_opts_a = {
                'format': 'bestaudio/best',
                'outtmpl': f'audio_{chat_id}',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
                'quiet': True
            }
            
            if "youtube" in url or "youtu.be" in url:
                ydl_opts_a['cookiefile'] = 'youtube.com_cookies.txt'
            
            await asyncio.to_thread(lambda: yt_dlp.YoutubeDL(ydl_opts_a).download([url]))
            
            final_audio = f'audio_{chat_id}.mp3'
            if os.path.exists(final_audio):
                with open(final_audio, 'rb') as a_file:
                    await update.message.reply_audio(audio=a_file, caption="🎵 تم استخراج الصوت")
                os.remove(final_audio)
        except Exception as audio_err:
            print(f"Audio Error: {audio_err}")
            await update.message.reply_text("⚠️ الفيديو وصل، لكن استخراج الصوت فشل (تأكد من اكتمال تنصيب ffmpeg على السيرفر)")

        await msg.delete()
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}\n(قد يكون حجم الفيديو كبيراً جداً حتى بعد الضغط)")
    finally:
        # تنظيف الملفات
        if os.path.exists(video_file): os.remove(video_file)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    application.run_polling()

if __name__ == '__main__':
    main()
