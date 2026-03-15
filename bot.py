import os
import asyncio
import subprocess
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [Operational Parameters] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso'

def update_system():
    """تحديث قسري لكسر تشفير يوتيوب الجديد"""
    try:
        subprocess.check_call(["pip", "install", "--upgrade", "yt-dlp"])
    except: pass

update_system()

# إعدادات الاختراق (قوة نارية مستهدفة)
YDL_OPTS_YT = {
    'format': 'best[ext=mp4]/best', # تجاوز FFmpeg
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'nocheckcertificate': True,
    # السر الناري: استخدام عملاء متعددين لتضليل نظام الحماية
    'extractor_args': {
        'youtube': {
            'player_client': ['android_test', 'web_embedded', 'tvhtml5embedded'],
            'player_skip': ['webpage', 'configs'],
        }
    },
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
        'Accept': '*/*',
    }
}

YDL_OPTS_TT = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🜄🜏 جاهز للاختراق سيدي المطور 🔥\n✅ تيك توك: صوت\n✅ يوتيوب: فيديو")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⚡ جاري اختراق حماية يوتيوب وسحب الفيديو...")

    is_tiktok = "tiktok.com" in url
    opts = YDL_OPTS_TT if is_tiktok else YDL_OPTS_YT

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(opts) as ydl:
            # محاولة الاستخراج مع تجاوز الحظر
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if os.path.exists(file_path):
            if is_tiktok:
                with open(file_path, 'rb') as audio:
                    await context.bot.send_audio(chat_id=chat_id, audio=audio, caption="✅ صوت تيك توك", reply_markup=reply_markup)
            else:
                with open(file_path, 'rb') as video:
                    await context.bot.send_video(chat_id=chat_id, video=video, caption="✅ فيديو يوتيوب مخترق", reply_markup=reply_markup, supports_streaming=True)
        
        await status_msg.delete()

    except Exception as e:
        print(f"Crit Error: {e}")
        # إذا فشل، نقوم بتحديث المكتبة فوراً للمحاولة القادمة
        update_system()
        await update.message.reply_text("❌ يوتيوب قام بصد الهجوم. تم تحديث أسلحتنا، كرر المحاولة الآن.")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        await asyncio.sleep(2)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                base = os.path.splitext(file_path)[0]
                for ext in ['.part', '.ytdl', '.mp4', '.m4a']:
                    if os.path.exists(base + ext): os.remove(base + ext)
            except: pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    app.run_polling()

if __name__ == '__main__':
    main()
