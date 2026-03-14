import os
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters, CommandHandler

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

LOADING_STICKER = "CAACAgIAAxkBAAIBQ2X"

def clean_files():
    for f in os.listdir():
        if f.endswith((".mp4", ".mp3", ".mkv", ".webm")):
            try:
                os.remove(f)
            except:
                pass


def download_video(url):

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": "video.%(ext)s",
        "quiet": True,
        "retries": 10
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def extract_audio(url):

    audio_opts = {
        "format": "bestaudio/best",
        "outtmpl": "audio.%(ext)s",
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    }

    with yt_dlp.YoutubeDL(audio_opts) as ydl:
        ydl.download([url])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "أرسل أي رابط فيديو وسأقوم بتحميله."
    )


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    sticker = await update.message.reply_sticker(LOADING_STICKER)

    try:

        video_file = await asyncio.to_thread(download_video, url)

        if os.path.exists(video_file):
            with open(video_file, "rb") as f:
                await update.message.reply_video(f)

        await asyncio.to_thread(extract_audio, url)

        if os.path.exists("audio.mp3"):
            with open("audio.mp3", "rb") as f:
                await update.message.reply_audio(f)

    except Exception as e:

        await update.message.reply_text("❌ فشل التحميل")

    clean_files()

    try:
        await sticker.delete()
    except:
        pass


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()
