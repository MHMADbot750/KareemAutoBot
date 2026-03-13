import os
import time
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ChatAction

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
LOADING_STICKER = "CAACAgIAAxkBAAIBQ2X"

# دالة التحميل مع خيارات دمج قوية
def ytdl_download(url, filename, fmt):
    opts = {
        "format": f"{fmt}+bestaudio/best/best",
        "outtmpl": filename,
        "quiet": True,
        "noplaylist": True,
        "merge_output_format": "mp4",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً كريم! أرسل رابط يوتيوب أو تيك توك.")

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
            await update.message.reply_text(f"خطأ: {e}")
    elif "tiktok.com" in url:
        # كود التيك توك (نفس المنطق)
        pass

async def download_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, fmt, url = query.data.split("|")
    sticker = await query.message.reply_sticker(LOADING_STICKER)
    filename = f"vid_{query.from_user.id}.mp4"

    try:
        # إظهار حالة "يرفع فيديو" في تليجرام
        await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.UPLOAD_VIDEO)
        
        await asyncio.to_thread(ytdl_download, url, filename, fmt)
        
        if os.path.exists(filename):
            with open(filename, "rb") as v:
                # أضفنا هنا التوقيتات العالية (Timeouts) لمنع انقطاع الاتصال
                await query.message.reply_video(
                    video=v, 
                    caption="تم التحميل بنجاح ✅",
                    read_timeout=300, 
                    write_timeout=300
                )
            os.remove(filename)
        else:
            await query.message.reply_text("❌ لم يتم العثور على الملف.")
    except Exception as e:
        await query.message.reply_text(f"❌ فشل الإرسال: {e}")
    finally:
        await sticker.delete()

def main():
    # تعديل الـ Application لتتحمل الشبكة الضعيفة
    app = ApplicationBuilder().token(TOKEN).read_timeout(30).write_timeout(30).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(download_quality, pattern="^yt"))
    app.run_polling()

if __name__ == "__main__":
    main()
