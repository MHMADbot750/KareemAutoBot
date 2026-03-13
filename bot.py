import os
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram.constants import ChatAction

# التوكن الخاص بك
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

def ytdl_download(url, filename, mode):
    if mode == "audio":
        # طلب أفضل جودة صوت بصيغة m4a مباشرة لتجنب الحاجة للتحويل بـ ffmpeg
        opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": filename,
            "noplaylist": True,
            "quiet": True
        }
    else:
        # طلب أفضل جودة فيديو مدمجة بصيغة mp4
        opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": filename,
            "noplaylist": True,
            "quiet": True
        }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        return

    user_id = update.message.from_user.id
    status_msg = await update.message.reply_text("⏳ جاري تحضير الفيديو والصوت معاً... انتظر قليلاً")

    try:
        # 1. تحميل وإرسال الفيديو
        video_file = f"vid_{user_id}.mp4"
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_VIDEO)
        await asyncio.to_thread(ytdl_download, url, video_file, "video")
        
        if os.path.exists(video_file):
            with open(video_file, "rb") as v:
                await update.message.reply_video(video=v, caption="تم تحميل الفيديو بنجاح ✅")
            os.remove(video_file)

        # 2. تحميل وإرسال الصوت تلقائياً بعد الفيديو
        audio_file_base = f"aud_{user_id}"
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_VOICE)
        await asyncio.to_thread(ytdl_download, url, audio_file_base, "audio")
        
        # البحث عن الملف الصوتي الناتج (سواء m4a أو mp3 أو webm)
        for ext in [".m4a", ".mp3", ".webm"]:
            full_path = audio_file_base + ext
            if os.path.exists(full_path):
                with open(full_path, "rb") as a:
                    await update.message.reply_audio(audio=a, caption="تم استخراج الصوت تلقائياً 🎵")
                os.remove(full_path)
                break

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"❌ فشل التحميل: {str(e)[:100]}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("البوت يعمل الآن يا كريم... أرسل رابطاً للتجربة")
    app.run_polling()
