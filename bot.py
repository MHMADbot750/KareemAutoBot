import os
import asyncio
import yt_dlp
import shutil
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# إعدادات متطورة لتجاوز حظر السيرفرات
YDL_OPTS = {
    'format': 'best', 
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ نظام Kareem Auto جاهز للعمل.\nأرسل الرابط الآن.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    status_msg = await update.message.reply_text("⏳ جاري التحميل ومعالجة الطلب...")

    # مجلد مؤقت نظيف لكل عملية
    temp_dir = f"work_{chat_id}_{int(asyncio.get_event_loop().time())}"
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)

    try:
        opts = YDL_OPTS.copy()
        opts['outtmpl'] = f'{temp_dir}/%(id)s.%(ext)s'

        with yt_dlp.YoutubeDL(opts) as ydl:
            # محاولة جلب المعلومات أولاً
            info = ydl.extract_info(url, download=True)
            
            # 1. التحقق من الصور (Slideshow)
            if 'entries' in info or info.get('formats') is None:
                images = info.get('requested_formats', []) or info.get('entries', [])
                img_urls = [i.get('url') for i in images if i.get('url')]
                if img_urls:
                    media = [InputMediaPhoto(u) for u in img_urls[:10]]
                    await context.bot.send_media_group(chat_id=chat_id, media=media)
            
            # 2. التحقق من الفيديو
            file_path = ydl.prepare_filename(info)
            if os.path.exists(file_path):
                # إرسال الفيديو
                with open(file_path, 'rb') as v:
                    await context.bot.send_video(chat_id=chat_id, video=v, caption="✅ الفيديو")
                # إرسال الصوت
                with open(file_path, 'rb') as a:
                    await context.bot.send_audio(chat_id=chat_id, audio=a, title="الصوت المستخرج")

        await status_msg.delete()

    except Exception as e:
        # إذا فشل التحميل، نعطي المستخدم رسالة واضحة ونطبع الخطأ في الـ Terminal
        await update.message.reply_text("⚠️ فشل في جلب البيانات من الموقع. تأكد من الرابط أو جرب لاحقاً.")
        print(f"DEBUG ERROR: {e}")
    
    finally:
        # التطهير الفوري للذاكرة
        await asyncio.sleep(5)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    app.run_polling()

if __name__ == '__main__':
    main()
