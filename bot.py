import os
import asyncio
import yt_dlp
import shutil
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [Operational Config] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# إعدادات متقدمة لجلب الصور والفيديو بدون FFmpeg
YDL_OPTS = {
    'format': 'best', 
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ نظام Kareem Auto مفعل.\n• تنزيل فيديو/صور تيك توك\n• استخراج الصوت تلقائياً\n• تنظيف الذاكرة فوري")

async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if "tiktok.com" not in url: return

    status_msg = await update.message.reply_text("⏳ جاري سحب المحتوى (فيديو/صور)...")

    # إنشاء منطقة عمل مؤقتة (تفريغ ذاكرة لاحق)
    worker_dir = f"task_{chat_id}_{int(asyncio.get_event_loop().time())}"
    if not os.path.exists(worker_dir): os.makedirs(worker_dir)

    try:
        opts = YDL_OPTS.copy()
        opts['outtmpl'] = f'{worker_dir}/%(id)s.%(ext)s'

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # --- [الذكاء الصناعي في التمييز بين الصور والفيديو] ---
            
            # 1. حالة صور تيك توك (Slideshow)
            if info.get('formats') is None or 'entries' in info or not info.get('duration'):
                # البحث عن روابط الصور في البيانات المستخرجة
                images = info.get('requested_formats', []) or info.get('entries', [])
                img_list = [i.get('url') for i in images if i.get('url')]
                
                if img_list:
                    # إرسال الصور كمجموعة (البوم)
                    media = [InputMediaPhoto(u) for u in img_list[:10]]
                    await context.bot.send_media_group(chat_id=chat_id, media=media)
                    # إرسال الصوت الخاص بالألبوم
                    audio_url = info.get('url') or info.get('webpage_url')
                    await context.bot.send_audio(chat_id=chat_id, audio=audio_url, title="صوت الصور")
            
            # 2. حالة الفيديو العادي
            else:
                file_path = ydl.prepare_filename(info)
                if os.path.exists(file_path):
                    # إرسال الفيديو
                    with open(file_path, 'rb') as v:
                        await context.bot.send_video(chat_id=chat_id, video=v, caption="✅ الفيديو جاهز")
                    # إرسcl الصوت تحت الفيديو مباشرة
                    with open(file_path, 'rb') as a:
                        await context.bot.send_audio(chat_id=chat_id, audio=a, title="الصوت المستخرج")

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text("⚠️ فشل في جلب البيانات. تأكد من تحديث نظام السيرفر.")
        print(f"Error Log: {e}")
    
    finally:
        # --- [بروتوكول تطهير الذاكرة] ---
        await asyncio.sleep(5) # انتظار الإرسال
        if os.path.exists(worker_dir):
            shutil.rmtree(worker_dir) # حذف المجلد والملفات نهائياً من السيرفر

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok))
    app.run_polling()

if __name__ == '__main__':
    main()
