import os
import asyncio
import yt_dlp
import shutil
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# إعدادات قوية لمحاكاة متصفح حقيقي وتفادي الحظر
YDL_OPTS = {
    'format': 'best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    # إضافة ميزة كسر التشفير عبر عملاء مختلفين
    'extractor_args': {'tiktok': {'app_version': '33.1.2', 'manifest_app_version': '33.1.2'}},
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 نظام Kareem Auto المحدث جاهز.\nأرسل رابط تيك توك (فيديو أو صور) الآن.")

async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if "tiktok.com" not in url: return

    status_msg = await update.message.reply_text("🔄 جاري محاولة كسر الحظر وسحب المحتوى...")

    process_dir = f"clean_task_{chat_id}"
    if not os.path.exists(process_dir): os.makedirs(process_dir)

    try:
        current_opts = YDL_OPTS.copy()
        current_opts['outtmpl'] = f'{process_dir}/%(id)s.%(ext)s'

        with yt_dlp.YoutubeDL(current_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # 1. إذا كان المحتوى "صور" (ألبوم)
            if info.get('duration') == 0 or 'entries' in info:
                images = info.get('requested_formats', []) or info.get('entries', [])
                img_urls = [i.get('url') for i in images if i.get('url')]
                if img_urls:
                    media = [InputMediaPhoto(u) for u in img_urls[:10]]
                    await context.bot.send_media_group(chat_id=chat_id, media=media)
            
            # 2. إذا كان المحتوى "فيديو"
            file_path = ydl.prepare_filename(info)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as v:
                    await context.bot.send_video(chat_id=chat_id, video=v, caption="✅ تم التحميل")
                with open(file_path, 'rb') as a:
                    await context.bot.send_audio(chat_id=chat_id, audio=a, title="الصوت")

        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text("❌ تيك توك حظر عنوان السيرفر. جاري المحاولة مرة أخرى...")
        print(f"Error Log: {e}")
    
    finally:
        # التطهير الفوري للذاكرة
        await asyncio.sleep(5)
        if os.path.exists(process_dir):
            shutil.rmtree(process_dir)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok))
    app.run_polling()

if __name__ == '__main__':
    main()
