import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:
        # =========================
        # تحميل الفيديو (يوتيوب أو تيك توك)
        # =========================
        video_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": "video.%(ext)s",
            "quiet": True
        }
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info)

        filesize = os.path.getsize(video_file)
        if filesize > 50 * 1024 * 1024:  # أكبر من 50 ميغا
            # إرسال الفيديو كمستند إذا أكبر من الحد
            with open(video_file, "rb") as f:
                await update.message.reply_document(f, filename=os.path.basename(video_file))
        else:
            with open(video_file, "rb") as f:
                await update.message.reply_video(f)

        os.remove(video_file)

        # =========================
        # تحميل الصوت
        # =========================
        audio_opts = {
            "format": "bestaudio/best",
            "outtmpl": "audio.%(ext)s",
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]
        }
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])

        # إرسال الصوت
        if os.path.exists("audio.mp3"):
            with open("audio.mp3", "rb") as f:
                await update.message.reply_audio(f)
            os.remove("audio.mp3")

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ فشل التحميل\n{e}")

# =========================
# تشغيل البوت
# =========================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot started")
app.run_polling()
