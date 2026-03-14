import os
import time
import subprocess
import yt_dlp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# -------------------- التوكن --------------------
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# -------------------- ملصق التحميل --------------------
LOADING_STICKER_ID = "CAACAgIAAxkBAAIBQ2X"  # غيّره إذا أحببت

# -------------------- حد الاستخدام لكل مستخدم --------------------
user_limits = {}  # {user_id: {"count": int, "time": timestamp}}
MAX_DOWNLOADS = 10
COOLDOWN = 86400  # 24 ساعة

def check_limit(user_id: int) -> bool:
    now = time.time()
    data = user_limits.get(user_id)
    if not data:
        user_limits[user_id] = {"count": 0, "time": now}
        data = user_limits[user_id]

    # إعادة الضبط بعد 24 ساعة
    if now - data["time"] >= COOLDOWN:
        data["count"] = 0
        data["time"] = now

    if data["count"] >= MAX_DOWNLOADS:
        return False

    data["count"] += 1
    return True

# -------------------- تنظيف الملفات القديمة --------------------
def clean():
    for f in os.listdir():
        if f.endswith((".mp4", ".mp3", ".webm", ".mkv")):
            try:
                os.remove(f)
            except:
                pass

# -------------------- تحديث yt-dlp تلقائي --------------------
subprocess.run(["pip", "install", "-U", "yt-dlp"])
subprocess.run(["apt","update"])
subprocess.run(["apt","install","-y","ffmpeg"])

# -------------------- دالة التحميل --------------------
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = (update.message.text or "").strip()
    user_id = update.message.from_user.id

    if not check_limit(user_id):
        await update.message.reply_text(
            f"❌ وصلت الحد اليومي ({MAX_DOWNLOADS} تنزيلات).\nارجع بعد 24 ساعة."
        )
        return

    sticker_msg = await update.message.reply_sticker(LOADING_STICKER_ID)

    try:
        clean()

        # -------------------- إعدادات الفيديو --------------------
        video_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": "video.%(ext)s",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(video_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info)

        # إرسال الفيديو
        if os.path.exists(video_file):
            with open(video_file, "rb") as f:
                await update.message.reply_video(f)

        # -------------------- إعدادات الصوت --------------------
        audio_opts = {
            "format": "bestaudio/best",
            "outtmpl": "audio.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }
            ],
        }

        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])

        # إرسال الصوت
        if os.path.exists("audio.mp3"):
            with open("audio.mp3","rb") as f:
                await update.message.reply_audio(f)

        clean()
        await sticker_msg.delete()

    except Exception as e:
        clean()
        try: await sticker_msg.delete()
        except: pass
        await update.message.reply_text(f"❌ فشل التحميل:\n{e}")

# -------------------- رسالة البداية --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أرسل رابط YouTube أو TikTok.\n"
        "• سيقوم البوت بتحميل الفيديو والصوت.\n"
        "• الحد اليومي لكل مستخدم: 10 تنزيلات.\n"
        "• الملفات تُحذف تلقائيًا بعد الإرسال."
    )

# -------------------- تشغيل البوت --------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
