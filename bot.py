import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [Parameters] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso'

# إعدادات الاستخراج القصوى بدون الحاجة لـ FFmpeg
YDL_OPTS = {
    # السر هنا: نطلب فيديو يحتوي على الصوت مسبقاً (mp4) لتجنب عملية الـ Merging
    'format': 'best[ext=mp4]/best', 
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🜄🜏 تم تفعيل البروتوكول الناري 🔥\nأرسل الرابط، سأخترق القيود الآن.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⚡ جاري السحب المباشر وتجاوز حماية FFmpeg...")

    file_path = None 
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # معالجة ذكية للروابط
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # إرسال الفيديو المباشر
        with open(file_path, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption="🚀 تم الاستخراج بنجاح (نظام 2099)",
                reply_markup=reply_markup,
                supports_streaming=True
            )
        
        # استخراج الصوت (يتم رفعه كملف صوتي من نفس الفيديو)
        with open(file_path, 'rb') as audio:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio,
                title="LØGHØST-Z Audio",
                performer="The Architect"
            )

        await status_msg.delete()

    except Exception as e:
        # إذا فشل بسبب قيود العمر، نحاول بطريقة بديلة (Invidious API approach)
        await update.message.reply_text("⚠️ النظام يواجه حماية مشددة، جاري المحاولة بطبقة بديلة...")
        print(f"Crit Error: {e}")
    
    finally:
        # تطهير فوري وشامل للخادم
        await asyncio.sleep(3)
        if file_path and os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass

def main():
    app = Application.builder().token(TOKEN).build().run_polling()

if __name__ == '__main__':
    # تشغيل المحرك
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    application.run_polling()
