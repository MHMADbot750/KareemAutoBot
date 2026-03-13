import os
import time
import yt_dlp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# ملصق متحرك أثناء التحميل (يمكن تغييره لأي sticker_id يعجبك)
LOADING_STICKER_ID = "CAACAgIAAxkBAAIBQ2X"  # غيّره لاحقًا إن أردت

# حد الاستخدام: 10 تنزيلات لكل مستخدم خلال 24 ساعة
user_limits = {}  # {user_id: {"count": int, "time": timestamp}}

def check_limit(user_id: int) -> bool:
    now = time.time()
    data = user_limits.get(user_id)

    if not data:
        user_limits[user_id] = {"count": 0, "time": now}
        data = user_limits[user_id]

    # إعادة الضبط بعد 24 ساعة
    if now - data["time"] >= 86400:
        data["count"] = 0
        data["time"] = now

    if data["count"] >= 10:
        return False

    data["count"] += 1
    return True


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = (update.message.text or "").strip()
    user_id = update.message.from_user.id

    if not check_limit(user_id):
        await update.message.reply_text(
            "❌ وصلت الحد اليومي (10 تنزيلات).\nارجع بعد 24 ساعة."
        )
        return

    # ------------------ YOUTUBE ------------------
    if "youtube.com" in url or "youtu.be" in url:
        try:
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
                    buttons.append(
                        [InlineKeyboardButton(f"{h}p", callback_data=f"yt|{fid}|{url}")]
                    )

            if not buttons:
                await update.message.reply_text("❌ لم أستطع جلب الدقات المتاحة.")
                return

            keyboard = InlineKeyboardMarkup(buttons[:8])
            await update.message.reply_text("اختر الدقة:", reply_markup=keyboard)

        except Exception as e:
            await update.message.reply_text(f"❌ خطأ:\n{e}")

    # ------------------ TIKTOK ------------------
    elif "tiktok.com" in url:
        sticker_msg = await update.message.reply_sticker(LOADING_STICKER_ID)

        try:
            # تحميل الفيديو
            video_opts = {
                "format": "best",
                "outtmpl": "video.mp4",
                "quiet": True,
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                ydl.download([url])

            # إرسال الفيديو
            if os.path.exists("video.mp4"):
                with open("video.mp4", "rb") as f:
                    await update.message.reply_video(f)
                os.remove("video.mp4")

            # استخراج الصوت MP3
            audio_opts = {
                "format": "bestaudio/best",
                "outtmpl": "audio.%(ext)s",
                "quiet": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([url])

            if os.path.exists("audio.mp3"):
                with open("audio.mp3", "rb") as f:
                    await update.message.reply_audio(f)
                os.remove("audio.mp3")

        except Exception as e:
            await update.message.reply_text(f"❌ فشل التحميل:\n{e}")

        finally:
            try:
                await sticker_msg.delete()
            except:
                pass

    else:
        await update.message.reply_text(
            "أرسل رابط من YouTube أو TikTok فقط."
        )


async def download_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        _, format_id, url = query.data.split("|", 2)

        sticker_msg = await query.message.reply_sticker(LOADING_STICKER_ID)

        ydl_opts = {
            "format": format_id,
            "outtmpl": "ytvideo.mp4",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists("ytvideo.mp4"):
            with open("ytvideo.mp4", "rb") as f:
                await query.message.reply_video(f)
            os.remove("ytvideo.mp4")

        try:
            await sticker_msg.delete()
        except:
            pass

    except Exception as e:
        await query.message.reply_text(f"❌ خطأ:\n{e}")


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
