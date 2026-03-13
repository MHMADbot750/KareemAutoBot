import os
import time
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# التوكن الخاص بك
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
LOADING_STICKER = "CAACAgIAAxkBAAIBQ2X"

user_limits = {}

def check_limit(user_id):
    now = time.time()
    data = user_limits.get(user_id)
    if not data:
        user_limits[user_id] = {"count": 0, "time": now}
        data = user_limits[user_id]
    if now - data["time"] > 86400:
        data["count"] = 0
        data["time"] = now
    if data["count"] >= 10:
        return False
    data["count"] += 1
    return True

# --- تعديل دالة التحميل لتكون أكثر استقراراً ---
def ytdl_download(url, filename, fmt):
    opts = {
        # 'best' تضمن تحميل فيديو وصوت مدمجين إذا لم يتوفر ffmpeg بشكل جيد
        "format": f"{fmt}+bestaudio/best", 
        "outtmpl": filename,
        "quiet": True,
        "noplaylist": True,
        "retries": 10,
        "merge_output_format": "mp4",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً كريم! أرسل رابط YouTube أو TikTok وسأقوم بالتحميل لك فوراً."
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    user_id = update.message.from_user.id

    if not check_limit(user_id):
        await update.message.reply_text("❌ وصلت الحد اليومي (10 تنزيلات)")
        return

    if "youtube.com" in url or "youtu.be" in url:
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)
            
            buttons = []
            seen = set()
            # تصفية الصيغ لاختيار الدقة التي تحتوي على فيديو وصوت
            for f in info.get("formats", []):
                h = f.get("height")
                if h and h not in seen and h <= 720: # حددنا الـ 720 لضمان الحجم
                    seen.add(h)
                    buttons.append([InlineKeyboardButton(f"{h}p", callback_data=f"yt|{f['format_id']}|{url}")])

            keyboard = InlineKeyboardMarkup(buttons[:8])
            await update.message.reply_text("اختر الدقة المطلوبة:", reply_markup=keyboard)
        except Exception as e:
            await update.message.reply_text(f"حدث خطأ في جلب المعلومات: {e}")

    elif "tiktok.com" in url or "vt.tiktok.com" in url:
        sticker = await update.message.reply_sticker(LOADING_STICKER)
        try:
            # تحميل تيك توك
            fn = f"tiktok_{user_id}.mp4"
            await asyncio.to_thread(ytdl_download, url, fn, "best")
            if os.path.exists(fn):
                await update.message.reply_video(video=open(fn, "rb"))
                os.remove(fn)
        except Exception as e:
            await update.message.reply_text(f"❌ فشل تحميل تيك توك: {e}")
        await sticker.delete()

async def download_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    _, fmt, url = query.data.split("|")
    sticker = await query.message.reply_sticker(LOADING_STICKER)
    user_id = query.from_user.id
    filename = f"video_{user_id}.mp4"

    try:
        # محاولة التحميل
        await asyncio.to_thread(ytdl_download, url, filename, fmt)
        
        if os.path.exists(filename):
            await query.message.reply_video(video=open(filename, "rb"), caption="تم التحميل بواسطة بوت كريم ✅")
            os.remove(filename)
        else:
            await query.message.reply_text("❌ فشل العثور على الملف المحمل.")
    except Exception as e:
        await query.message.reply_text(f"خطأ أثناء التحميل: {e}")
    
    await sticker.delete()

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(download_quality, pattern="^yt"))
    print("البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()
