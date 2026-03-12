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

    msg = await update.message.reply_text("⏳ جاري محاولة تجاوز الحماية والتحميل...")

    # إعدادات متقدمة جداً لتخطي رسالة "Sign in to confirm"
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': 'file_%(id)s.%(ext)s',
        # هذه الأسطر هي السر لتجاوز الحظر:
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.android.youtube/19.29.37 (Linux; U; Android 11) gzip',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # استخراج المعلومات والتحميل في خطوة واحدة
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            # إرسال الملف (فيديو)
            with open(filename, "rb") as f:
                await update.message.reply_video(video=f, caption="✅ تم التحميل بنجاح عبر نظام Android Bypass")

            # حذف الملف
            os.remove(filename)
            await msg.delete()

    except Exception as e:
        # إذا فشل، نحاول تحميل الصوت فقط كخطة بديلة
        await msg.edit_text(f"⚠️ يوتيوب لا يزال يمنع السيرفر. الحل البديل هو تحديث ملف المكتبة في Railway.\n\nالخطأ الحالي:\n{str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    print("البوت يعمل بنظام التجاوز...")
    app.run_polling()
