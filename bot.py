import os
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram.constants import ChatAction

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

def ytdl_download(url, filename, mode):
    if mode == "audio":
        # حل مشكلة الصوت: نطلب صيغة m4a مباشرة لأنها لا تحتاج تحويل أو ffmpeg
        opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": filename,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }
    else:
        # حل مشكلة الفيديو: نطلب ملف MP4 جاهز لتجنب عملية الـ Merging التي تتطلب ffmpeg
        opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": filename,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        return

    # فحص روابط تيك توك التي تكون عبارة عن صور (Photo Mode) لأنها تسبب فشلاً
    if "tiktok.com" in url and "/photo/" in url:
        await update.message.reply_text("⚠️ عذراً، هذا الرابط عبارة عن 'صور' وليس فيديو. البوت يدعم الفيديوهات فقط حالياً.")
        return

    user_id = update.message.from_user.id
    status_msg = await update.message.reply_text("⏳ جاري استخراج الفيديو والصوت تلقائياً...")

    try:
        # 1. محاولة إرسال الفيديو أولاً
        video_file = f"vid_{user_id}.mp4"
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_VIDEO)
        
        try:
            await asyncio.to_thread(ytdl_download, url, video_file, "video")
            if os.path.exists(video_file):
                with open(video_file, "rb") as v:
                    await update.message.reply_video(video=v, caption="✅ تم تحميل الفيديو")
                os.remove(video_file)
        except Exception as ve:
            print(f"Video Error: {ve}")

        # 2. استخراج الصوت تلقائياً وإرساله تحت الفيديو
        audio_file_base = f"aud_{user_id}"
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_VOICE)
        
        # نرسل اسم الملف بدون صيغة ليدع yt-dlp يختار الأنسب (m4a أو mp3)
        await asyncio.to_thread(ytdl_download, url, audio_file_base + ".%(ext)s", "audio")
        
        # البحث عن أي ملف صوتي نتج عن العملية
        found = False
        for ext in [".m4a", ".mp3", ".webm", ".aac"]:
            full_path = audio_file_base + ext
            if os.path.exists(full_path):
                with open(full_path, "rb") as a:
                    await update.message.reply_audio(audio=a, caption="🎵 تم استخراج الصوت تلقائياً")
                os.remove(full_path)
                found = True
                break
        
        if not found:
            await update.message.reply_text("❌ لم نتمكن من استخراج الصوت لهذا الرابط تحديداً.")

        await status_msg.delete()

    except Exception as e:
        error_text = str(e)
        if "Unsupported URL" in error_text:
            await status_msg.edit_text("❌ الرابط غير مدعوم أو هو عبارة عن 'صور' تيك توك.")
        else:
            await status_msg.edit_text(f"❌ حدث خطأ: {error_text[:50]}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.run_polling()
