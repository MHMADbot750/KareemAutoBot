import os
import time
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ChatAction

# التوكن الخاص بك
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
LOADING_STICKER = "CAACAgIAAxkBAAIBQ2X"

# دالة التحميل مع ضمان دمج الصوت والفيديو
def ytdl_download(url, filename, fmt):
    opts = {
        "format": f"{fmt}+bestaudio/best/best",
        "outtmpl": filename,
        "quiet": True,
        "noplaylist": True,
        "merge_output_format": "mp4",
        "postprocessor_args": ['-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental']
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً كريم! أرسل رابط يوتيوب أو تيك توك وسأبدأ التحميل.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "youtube.com" in url or "youtu.be" in url:
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)
            buttons = []
            seen = set()
            for f in info.get("formats", []):
                h = f.get("height")
                if h and h not in seen and h <= 720:
                    seen.add(h)
                    buttons.append([InlineKeyboardButton(f"{h}p", callback_data=f"yt|{f['format_id']}|{url}")])
            await update.message.reply_text("اختر الدقة:", reply_markup=InlineKeyboardMarkup(buttons[:8]))
        except Exception as e:
            await update.message.reply_text(f"خطأ في الرابط: {e}")
    elif "tiktok.com" in url:
        # يمكنك إضافة منطق التيك توك هنا لاحقاً بنفس الطريقة
        pass

async def download_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, fmt, url = query.data.split("|")
    sticker = await query.message.reply_sticker(LOADING_STICKER)
    filename = f"vid_{query.from_user.id}.mp4"

    try:
        # إظهار حالة "جاري الرفع"
        await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.UPLOAD_VIDEO)
        
        # التحميل في خلفية البوت
        await asyncio.to_thread(ytdl_download, url, filename, fmt)
        
        if os.path.exists(filename):
            with open(filename, "rb") as v:
                # إرسال الفيديو مع زيادة وقت الانتظار يدوياً داخل الدالة
                await query.message.reply_video(
                    video=v, 
                    caption="تم التحميل بنجاح ✅\nبواسطة بوت كريم",
                    connect_timeout=60,
                    read_timeout=300,
                    write_timeout=300
                )
            os.remove(filename)
        else:
            await query.message.reply_text("❌ عذراً، لم أستطع إيجاد الملف بعد تحميله.")
    except Exception as e:
        await query.message.reply_text(f"❌ حدث خطأ أثناء الإرسال: {e}")
    finally:
        await sticker.delete()

def main():
    # تعديل طريقة بناء التطبيق لتلافي خطأ الـ TypeError
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(download_quality, pattern="^yt"))
    
    print("البوت يعمل الآن يا كريم...")
    app.run_polling()

if __name__ == "__main__":
    main()
