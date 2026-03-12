import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# التوكن الخاص بك
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    # التحقق من أن النص هو رابط فعلاً
    if not url.startswith(("http://", "https://")):
        return

    msg = await update.message.reply_text("⏳ جاري معالجة الرابط واستخراج الملفات...")

    try:
        # إعدادات تحميل الفيديو (اختيار صيغة جاهزة مدمجة الصوت لتجنب مشاكل ffmpeg)
        ydl_opts_video = {
            "format": "best", 
            "outtmpl": "video_%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
        }

        # إعدادات تحميل الصوت (بصيغته الأصلية لضمان السرعة والعمل بدون تحويل)
        ydl_opts_audio = {
            "format": "bestaudio/best",
            "outtmpl": "audio_%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
        }

        # تنفيذ تحميل الفيديو
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info)

        # تنفيذ تحميل الصوت
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            info_audio = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(info_audio)

        # إرسال الملفات للمستخدم
        with open(video_file, "rb") as v_file:
            await update.message.reply_video(video=v_file, caption="🎬 تم تحميل الفيديو")
        
        with open(audio_file, "rb") as a_file:
            await update.message.reply_audio(audio=a_file, caption="🎵 تم استخراج الصوت")

        # حذف الملفات من السيرفر بعد الإرسال لتوفير المساحة
        if os.path.exists(video_file): os.remove(video_file)
        if os.path.exists(audio_file): os.remove(audio_file)
        
        await msg.delete()

    except Exception as e:
        # في حال حدوث خطأ، سيتم تعديل الرسالة لتوضيح السبب
        await msg.edit_text(f"❌ حدث خطأ أثناء التحميل:\n\n{str(e)}")

# تشغيل البوت
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    
    print("البوت يعمل الآن... (KareemAutoBot)")
    app.run_polling()
