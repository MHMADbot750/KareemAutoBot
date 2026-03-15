import os
import asyncio
import subprocess
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- [الإعدادات الأمنية القصوى] ---
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
DEVELOPER_URL = 'https://t.me/ll3lso'

# 1. نظام التحديث التلقائي الإجباري لضمان كسر الحماية يومياً
def auto_upgrade():
    try:
        subprocess.check_call(["pip", "install", "--upgrade", "yt-dlp"])
    except:
        pass

auto_upgrade()

# 2. إعدادات "الاختراق الشامل" (تدمير قيود FFmpeg والحظر)
YDL_OPTS = {
    # دمج ذكي: نطلب أفضل ملف جاهز (mp4) لتجنب الحاجة لـ FFmpeg نهائياً
    'format': 'best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    
    # محاكاة "هوية الأجهزة الذكية" (تجاوز حظر يوتيوب وتيك توك)
    'extractor_args': {
        'youtube': {'player_client': ['ios', 'android']},
        'tiktok': {'app_version': '33.3.4'}
    },
    
    # بصمة متصفح عابرة للأبعاد
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        'Accept': '*/*',
        'Referer': 'https://www.google.com/',
        'Accept-Language': 'en-US,en;q=0.9',
    },
    'cookiefile': 'cookies.txt' # إذا كان لديك ملف كوكيز، ضعه هنا لكسر المستحيل
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🜄🜏 تم تفعيل البروتوكول الناري 🔥\nنحن في وضع الهجوم الكامل. أرسل الرابط الآن.")

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    if not url.startswith("http"): return

    status_msg = await update.message.reply_text("⚡ جاري كسر التشفير وتجاوز قيود الخادم...")

    file_path = None 
    try:
        # إنشاء مجلد التحميل إذا لم يكن موجوداً
        if not os.path.exists('downloads'): os.makedirs('downloads')

        # تنفيذ الهجوم لسحب الملف
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        keyboard = [[InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # إرسال الفيديو (سيعمل على يوتيوب، تيك توك، فيسبوك، انستغرام)
        with open(file_path, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption="🚀 تمت المهمة بنجاح سيدي المطور",
                reply_markup=reply_markup,
                supports_streaming=True
            )
        
        # استخراج الصوت كطبقة ثانية تحت الفيديو
        with open(file_path, 'rb') as audio:
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=audio,
                title="System Sound Trace",
                performer="LØGHØST-Z"
            )

        await status_msg.delete()

    except Exception as e:
        # في حال حدوث خطأ، نقوم بتحديث المكتبة فوراً للمحاولة القادمة
        auto_upgrade()
        await update.message.reply_text(f"⚠️ حماية الموقع قوية جداً. تم تحديث أسلحتنا، حاول إرسال الرابط مرة أخرى.")
        print(f"Bypass Trace: {e}")
        if 'status_msg' in locals(): await status_msg.delete()
    
    finally:
        # 3. تطهير الذاكرة الفوري (حماية الخادم المجاني)
        await asyncio.sleep(2)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                # حذف أي ملفات مؤقتة متبقية
                base = os.path.splitext(file_path)[0]
                for ext in ['.part', '.ytdl', '.temp', '.mp4']:
                    if os.path.exists(base + ext): os.remove(base + ext)
            except: pass

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_download))
    application.run_polling()

if __name__ == '__main__':
    main()
