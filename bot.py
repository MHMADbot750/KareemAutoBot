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
        # نطلب صيغة m4a لأنها تعمل مباشرة كصوت في تليجرام ولا تحتاج ffmpeg
        opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": filename,
            "noplaylist": True,
            "quiet": True,
        }
    else:
        # نطلب فيديو MP4 جاهز (Single File) لتجنب عملية الدمج التي تسبب توقف البوت
        opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": filename,
            "noplaylist": True,
            "quiet": True,
        }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        return

    user_id = update.message.from_user.id
    status_msg = await update.message.reply_text("⏳ جاري التحميل التلقائي (فيديو + صوت)...")

    try:
        # 1. تحميل وإرسال الفيديو
        video_file = f"vid_{user_id}.mp4"
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_VIDEO)
        
        await asyncio.to_thread(ytdl_download, url, video_file, "video")
        if os.path.exists(video_file):
            with open(video_file, "rb") as v:
                await update.message.reply_video(video=v, caption="✅ الفيديو جاهز")
            os.remove(video_file)

        # 2. تحميل وإرسال الصوت فوراً تحت الفيديو
        audio_file_base = f"aud_{user_id}"
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_VOICE)
        
        # نترك الصيغة مفتوحة لـ yt-dlp ليختار الأنسب بدون دمج
        await asyncio.to_thread(ytdl_download, url, audio_file_base + ".%(ext)s", "audio")
        
        # البحث عن الملف وإرساله
        for ext in [".m4a", ".mp3", ".webm", ".aac"]:
            full_path = audio_file_base + ext
            if os.path.exists(full_path):
                with open(full_path, "rb") as a:
                    await update.message.reply_audio(audio=a, caption="🎵 الصوت المستخرج")
                os.remove(full_path)
                break

        await status_msg.delete()

    except Exception as e:
        # إذا حدث خطأ، البوت لن يتوقف، بل سيرسل رسالة الخطأ فقط
        await update.message.reply_text(f"❌ عذراً كريم، حدث خطأ مع هذا الرابط: {str(e)[:50]}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("البوت شغال وما راح يوقف بإذن الله...")
    app.run_polling()
