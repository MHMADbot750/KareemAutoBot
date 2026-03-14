import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
CHANNEL_URL = 'https://t.me/ll3lso'

# إعدادات متطورة لتجاوز قيود تيك توك وانستقرام
YDL_OPTS = {
    'format': 'best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    # إضافة User-Agent ليوهم الموقع أن البوت متصفح حقيقي
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'referer': 'https://www.tiktok.com/',
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت شغال! أرسل الرابط وماراح يخيب ظنك.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⏳ جاري التحميل... انتظر ثواني")

    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # محاولة التحميل مع معالجة الأخطاء
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # الأزرار كما طلبتها بالضبط
        keyboard = [
            [InlineKeyboardButton("🎵 FindMusic Spotify", url="https://t.me/FindMusicSpotify")],
            [InlineKeyboardButton("🛑 YouTube download bot", url="https://t.me/YoutubeDownloadBot")],
            [InlineKeyboardButton("👨‍💻 المطور", url=CHANNEL_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # إرسال الفيديو
        with open(file_path, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption="✅ تم التحميل بنجاح",
                reply_markup=reply_markup
            )

        # إرسال الصوت
        with open(file_path, 'rb') as audio:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio,
                title="الصوت المستخرج",
                performer="Kareem Auto"
            )

        await status_msg.delete()

    except Exception as e:
        # إذا واجه مشكلة تسجيل الدخول مرة ثانية، راح يعطيك رسالة أوضح
        await update.message.reply_text("❌ عذراً، هذا الرابط محمي أو يحتاج تحديث للمكتبة.")
        print(f"Error: {e}")
    
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    app.run_polling()

if __name__ == '__main__':
    main()
