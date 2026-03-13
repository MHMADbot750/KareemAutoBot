import os
import yt_dlp
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQueryHandler

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

user_limits = {}

# حد التنزيل اليومي
def check_limit(user_id):
    now = time.time()

    if user_id not in user_limits:
        user_limits[user_id] = {"count":0,"time":now}

    data = user_limits[user_id]

    if now - data["time"] > 86400:
        data["count"] = 0
        data["time"] = now

    if data["count"] >= 10:
        return False

    data["count"] += 1
    return True


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text
    user_id = update.message.from_user.id

    if not check_limit(user_id):
        await update.message.reply_text("❌ وصلت الحد اليومي 10 تحميلات\nارجع بعد 24 ساعة")
        return

    if "youtube.com" in url or "youtu.be" in url:

        ydl_opts = {"quiet":True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        buttons = []

        for f in info["formats"]:
            if f.get("height"):
                text = f'{f["height"]}p'
                buttons.append([InlineKeyboardButton(text,callback_data=f"{url}|{f['format_id']}")])

        keyboard = InlineKeyboardMarkup(buttons[:6])

        await update.message.reply_text("اختر الدقة",reply_markup=keyboard)


    elif "tiktok.com" in url:

        sticker = await update.message.reply_sticker("CAACAgIAAxkBAAIBQ2X")  # ملصق متحرك

        try:

            video_opts = {
                "format":"best",
                "outtmpl":"video.mp4",
                "quiet":True
            }

            with yt_dlp.YoutubeDL(video_opts) as ydl:
                ydl.download([url])

            with open("video.mp4","rb") as f:
                await update.message.reply_video(f)

            os.remove("video.mp4")

            audio_opts = {
                "format":"bestaudio/best",
                "outtmpl":"audio.%(ext)s",
                "postprocessors":[{
                    "key":"FFmpegExtractAudio",
                    "preferredcodec":"mp3",
                    "preferredquality":"192"
                }]
            }

            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([url])

            with open("audio.mp3","rb") as f:
                await update.message.reply_audio(f)

            os.remove("audio.mp3")

        except Exception as e:
            await update.message.reply_text(f"فشل التحميل\n{e}")

        await sticker.delete()



async def download_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data.split("|")
    url = data[0]
    format_id = data[1]

    try:

        ydl_opts = {
            "format":format_id,
            "outtmpl":"video.mp4",
            "quiet":True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open("video.mp4","rb") as f:
            await query.message.reply_video(f)

        os.remove("video.mp4")

    except Exception as e:
        await query.message.reply_text(f"خطأ\n{e}")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(download_quality))

print("BOT RUNNING")

app.run_polling()
