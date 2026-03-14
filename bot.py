import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"
LOADING_STICKER_ID = "CAACAgIAAxkBAAIBQ2X"  # غيّر للملصق اللي تحبه

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    sticker = await update.message.reply_sticker(LOADING_STICKER_ID)

    try:
        if "youtube.com" in url or "youtu.be" in url:
            ydl_opts = {"quiet": True, "noplaylist": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            buttons = []
            seen = set()
            for f in info.get("formats", []):
                h = f.get("height")
                fid = f.get("format_id")
                if h and fid and h not in seen:
                    seen.add(h)
                    buttons.append([InlineKeyboardButton(f"{h}p", callback_data=f"yt|{fid}|{url}")])
            
            keyboard = InlineKeyboardMarkup(buttons[:8])
            await update.message.reply_text("اختر الدقة:", reply_markup=keyboard)

        elif "tiktok.com" in url:
            # تحميل الفيديو
            video_opts = {"format": "best", "outtmpl": "video.mp4", "quiet": True, "noplaylist": True}
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                ydl.download([url])
            
            # إرسال الفيديو
            if os.path.exists("video.mp4"):
                with open("video.mp4", "rb") as f:
                    await update.message.reply_video(f)
                os.remove("video.mp4")
            
            # استخراج الصوت
            audio_opts = {
                "format": "bestaudio/best",
                "outtmpl": "audio.%(ext)s",
                "quiet": True,
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
            }
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([url])

            if os.path.exists("audio.mp3"):
                with open("audio.mp3", "rb") as f:
                    await update.message.reply_audio(f)
                os.remove("audio.mp3")
        else:
            await update.message.reply_text("أرسل رابط من YouTube أو TikTok فقط.")
    
    except Exception as e:
        await update.message.reply_text(f"❌ فشل التحميل:\n{e}")
    
    finally:
        try: await sticker.delete()
        except: pass

async def download_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, format_id, url = query.data.split("|", 2)
    
    sticker = await query.message.reply_sticker(LOADING_STICKER_ID)
    ydl_opts = {"format": format_id, "outtmpl": "ytvideo.mp4", "quiet": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    if os.path.exists("ytvideo.mp4"):
        with open("ytvideo.mp4", "rb") as f:
            await query.message.reply_video(f)
        os.remove("ytvideo.mp4")
    
    try: await sticker.delete()
    except: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أرسل رابط YouTube أو TikTok.\n"
        "• YouTube: سيظهر اختيار الدقة.\n"
        "• TikTok: سأرسل الفيديو ثم الصوت."
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(download_quality, pattern="^yt\\|"))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
