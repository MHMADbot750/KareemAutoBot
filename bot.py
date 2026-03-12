import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith(("http://", "https://")):
        return

    msg = await update.message.reply_text("⏳ جاري محاولة فك التشفير والتحميل...")

    # إعدادات متقدمة لتخطي حظر يوتيوب
    common_opts = {
        "quiet": True,
        "noplaylist": True,
        "no_warnings": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "referer": "https://www.google.com/",
        "extract_flat": False,
    }

    try:
        # تحميل الفيديو
        ydl_opts_video = {
            **common_opts,
            "format": "best", 
            "outtmpl": "video_%(id)s.%(ext)s",
        }

        # تحميل الصوت
        ydl_opts_audio = {
            **common_opts,
            "format": "bestaudio/best",
            "outtmpl": "audio_%(id)s.%(ext)s",
        }

        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info)

        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            info_audio = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(info_audio)

        # إرسال الملفات
        with open(video_file, "rb") as v_file:
            await update.message.reply_video(video=v_file, caption="🎬 تم التحميل بنجاح")
        
        with open(audio_file, "rb") as a_file:
            await update.message.reply_audio(audio=a_file, caption="🎵 ملف الصوت")

        # حذف الملفات
        os.remove(video_file)
        os.remove(audio_file)
        await msg.delete()

    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Sign in to confirm" in error_msg:
            await msg.edit_text("❌ يوتيوب قام بحظر عنوان السيرفر مؤقتاً.\nجرب إرسال الرابط مرة أخرى بعد قليل.")
        else:
            await msg.edit_text(f"❌ حدث خطأ:\n{error_msg}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    print("البوت يعمل الآن...")
    app.run_polling()
