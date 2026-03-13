import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ChatAction

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

def ytdl_download(url, filename, mode):
    if mode == "audio":
        opts = {
            "format": "bestaudio/best",
            "outtmpl": filename.replace(".mp4", ".mp3"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
    else:
        # تحميل فيديو MP4 جاهز لتجنب مشاكل الدمج إذا تعطل ffmpeg
        opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": filename,
            "merge_output_format": "mp4",
        }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً كريم! أرسل رابط فيديو (يوتيوب أو تيك توك) واختيار فيديو أو صوت.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "http" in url:
        keyboard = [
            [InlineKeyboardButton("تحميل فيديو 🎬", callback_data=f"vid|{url}")],
            [InlineKeyboardButton("استخراج صوت 🎵", callback_data=f"aud|{url}")]
        ]
        await update.message.reply_text("اختر النوع:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode_type, url = query.data.split("|")
    
    status_msg = await query.message.reply_text("⏳ جاري المعالجة...")
    user_id = query.from_user.id
    
    try:
        if mode_type == "vid":
            filename = f"vid_{user_id}.mp4"
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.UPLOAD_VIDEO)
            await asyncio.to_thread(ytdl_download, url, filename, "video")
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    await query.message.reply_video(video=f, caption="تم بنجاح ✅", write_timeout=600)
                os.remove(filename)
            
        elif mode_type == "aud":
            filename = f"aud_{user_id}.mp3"
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.UPLOAD_VOICE)
            await asyncio.to_thread(ytdl_download, url, filename, "audio")
            final_audio = filename if os.path.exists(filename) else filename.replace(".mp4", ".mp3")
            if os.path.exists(final_audio):
                with open(final_audio, "rb") as f:
                    await query.message.reply_audio(audio=f, caption="تم استخراج الصوت 🎵", write_timeout=600)
                os.remove(final_audio)
        
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ خطأ: {str(e)[:100]}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
