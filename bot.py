import os
import time
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

LOADING_STICKER_ID = "CAACAgIAAxkBAAIBQ2X"

user_limits = {}

def check_limit(user_id):
    now = time.time()
    data = user_limits.get(user_id)

    if not data:
        user_limits[user_id] = {"count": 0, "time": now}
        data = user_limits[user_id]

    if now - data["time"] >= 86400:
        data["count"] = 0
        data["time"] = now

    if data["count"] >= 10:
        return False

    data["count"] += 1
    return True


def download_video(url, filename, format_code):
    opts = {
        "format": format_code,
        "outtmpl": filename,
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()
    user_id = update.message.from_user.id

    if not check_limit(user_id):
        await update.message.reply_text("❌ الحد اليومي 10 تنزيلات فقط")
        return

    # YOUTUBE
    if "youtube.com" in url or "youtu.be" in url:

        try:

            ydl_opts = {"quiet": True}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            buttons = []
            seen = set()

            for f in info["formats"]:
                h = f.get("height")
                fid = f.get("format_id")

                if h and fid and h not in seen:
                    seen.add(h)
                    buttons.append(
                        [InlineKeyboardButton(f"{h}p", callback_data=f"{fid}|{url}")]
                    )

            keyboard = InlineKeyboardMarkup(buttons[:8])

            await update.message.reply_text("اختر الدقة:", reply_markup=keyboard)

        except Exception as e:
            await update.message.reply_text(f"❌ خطأ {e}")


    # TIKTOK
    elif "tiktok.com" in url or "vt.tiktok.com" in url or "vm.tiktok.com" in url:

        sticker = await update.message.reply_sticker(LOADING_STICKER_ID)

        try:

            await asyncio.to_thread(download_video, url, "video.mp4", "best")

            with open("video.mp4", "rb") as f:
                await update.message.reply_video(f)

            os.remove("video.mp4")

            audio_opts = {
                "format": "bestaudio/best",
                "outtmpl": "audio.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3"
                }]
            }

            def dl():
                with yt_dlp.YoutubeDL(audio_opts) as ydl:
                    ydl.download([url])

            await asyncio.to_thread(dl)

            if os.path.exists("audio.mp3"):
                with open("audio.mp3", "rb") as f:
                    await update.message.reply_audio(f)
                os.remove("audio.mp3")

        except Exception as e:
            await update.message.reply_text(f"❌ فشل التحميل {e}")

        await sticker.delete()

    else:
        await update.message.reply_text("أرسل رابط YouTube أو TikTok فقط")


async def download_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    format_id, url = query.data.split("|")

    sticker = await query.message.reply_sticker(LOADING_STICKER_ID)

    try:

        await asyncio.to_thread(download_video, url, "ytvideo.mp4", format_id)

        with open("ytvideo.mp4", "rb") as f:
            await query.message.reply_video(f)

        os.remove("ytvideo.mp4")

    except Exception as e:
        await query.message.reply_text(f"❌ خطأ {e}")

    await sticker.delete()


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(download_quality))

    print("Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()
