import os
import asyncio
import subprocess
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [Core Setup] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso'

# وظيفة التحديث التلقائي للمكتبة (سلاحنا السري)
def update_library():
    try:
        subprocess.check_call(["pip", "install", "--upgrade", "yt-dlp"])
        print("🚀 [System] yt-dlp updated to the latest version.")
    except Exception as e:
        print(f"❌ [System] Update failed: {e}")

# استدعاء التحديث عند التشغيل
update_library()

# إعدادات كسر الأبعاد (Hyper-Bypass Settings)
YDL_OPTS = {
    'format': 'best[ext=mp4]/best', # تجاوز عدم وجود FFmpeg
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    
    # السر الجذري: استخدام واجهة iOS (حماية يوتيوب عليها هي الأضعف حالياً)
    'extractor_args': {
        'youtube': {
            'player_client': ['ios'],
        }
    },
    
    # تزوير الهوية البشرية القصوى
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🜄🜏 تم تفعيل البروتوكول النهائي 🔥\nالنظام يقوم بتحديث نفسه تلقائياً لمواجهة حماية يوتيوب.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⚡ جاري حقن البروتوكول وتجاوز حماية الـ IP...")

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        # محاولة التحميل باستخدام محاكي iOS
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as video:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=video,
                    caption="✅ تم الاختراق بنجاح (نسخة 2099 المحدثة)",
                    reply_markup=reply_markup,
                    supports_streaming=True
                )
            
            with open(file_path, 'rb') as audio:
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=audio,
                    title="Clean Trace",
                    performer="The Architect"
                )
        
        await status_msg.delete()

    except Exception as e:
        # إذا استمرت المشكلة، نقوم بمحاولة أخيرة بتحديث المكتبة فوراً
        update_library()
        await update.message.reply_text("⚠️ يوتيوب شدد الحماية. تم تحديث النظام تلقائياً، أرسل الرابط مرة أخرى.")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        await asyncio.sleep(2)
        if file_path and os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    application.run_polling()

if __name__ == '__main__':
    main()
