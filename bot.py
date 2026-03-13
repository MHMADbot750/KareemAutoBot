import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ChatAction

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# محاولة إضافة مسارات ffmpeg الشائعة في Railway
os.environ["PATH"] += os.pathsep + "/usr/bin" + os.pathsep + "/bin"

def ytdl_download(url, filename, mode):
    opts = {
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    if mode == "audio":
        opts.update({
            "format": "bestaudio/best",
            "outtmpl": filename,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        # تحميل فيديو MP4 جاهز لتجنب الحاجة للدمج في حال فشل ffmpeg
        opts.update({
            "format": "best[ext=mp4]/best",
            "outtmpl": filename,
        })
        
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "http" in url:
        keyboard = [
            [InlineKeyboardButton("🎬 تحميل فيديو", callback_data=f"vid|{url}")],
            [InlineKeyboardButton("🎵 استخراج صوت MP3", callback_data=f"aud|{url}")]
        ]
        await update.message.reply_text("اختر النوع المطلوب:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode, url = query.data.split("|")
    status = await query.message.reply_text("⏳ جاري المعالجة... يرجى الانتظار")
    
    try:
        if mode == "vid":
            fname = f"vid_{query.from_user.id}.mp4"
            await asyncio.to_thread(ytdl_download, url, fname, "video")
            if os.path.exists(fname):
                with open(fname, "rb") as f:
                    await query.message.reply_video(video=f, caption="تم التحميل بنجاح ✅")
                os.remove(fname)
        else:
            fname = f"aud_{query.from_user.id}.mp3"
            await asyncio.to_thread(ytdl_download, url, fname, "audio")
            if os.path.exists(fname):
                with open(fname, "rb") as f:
                    await query.message.reply_audio(audio=f, caption="تم استخراج الصوت 🎵")
                os.remove(fname)
        await status.delete()
    except Exception as e:
        await status.edit_text(f"❌ حدث خطأ: {str(e)[:150]}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()
