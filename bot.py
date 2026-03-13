import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ChatAction

# التوكن الخاص بك
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

# إجبار السيرفر على معرفة مكان ffmpeg (هذا السطر يحل مشكلة الإيرور الأخير)
os.environ["PATH"] += os.pathsep + "/usr/bin"

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
        # تحميل أفضل جودة فيديو وصوت مدمجين تلقائياً لتجنب الحاجة للدمج اليدوي
        opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": filename,
            "merge_output_format": "mp4",
        }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً كريم! أرسل رابط الفيديو وافتح القائمة لاختيار فيديو أو صوت.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "http" in url:
        keyboard = [
            [InlineKeyboardButton("تحميل فيديو 🎬", callback_data=f"vid|{url}")],
            [InlineKeyboardButton("استخراج صوت (MP3) 🎵", callback_data=f"aud|{url}")]
        ]
        await update.message.reply_text("ماذا تريد أن أفعل بالرابط؟", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    mode_type = data[0]
    url = data[1]
    
    status_msg = await query.message.reply_text("⏳ جاري العمل على طلبك... انتظر قليلاً.")
    user_id = query.from_user.id
    
    try:
        if mode_type == "vid":
            filename = f"video_{user_id}.mp4"
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.UPLOAD_VIDEO)
            await asyncio.to_thread(ytdl_download, url, filename, "video")
            
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    await query.message.reply_video(video=f, caption="تم تحميل الفيديو بنجاح ✅", write_timeout=600)
                os.remove(filename)
            
        elif mode_type == "aud":
            filename = f"audio_{user_id}.mp3"
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.UPLOAD_VOICE)
            await asyncio.to_thread(ytdl_download, url, filename, "audio")
            
            final_audio = filename.replace(".mp4", ".mp3")
            if os.path.exists(final_audio):
                with open(final_audio, "rb") as f:
                    await query.message.reply_audio(audio=f, caption="تم استخراج الصوت بنجاح 🎵", write_timeout=600)
                os.remove(final_audio)
        
        await status_msg.delete()
        
    except Exception as e:
        error_text = str(e)
        if "ffmpeg" in error_text.lower():
            await status_msg.edit_text("❌ مشكلة في السيرفر: أداة FFmpeg غير مفعلة بشكل صحيح. تأكد من إعدادات Railway.")
        else:
            await status_msg.edit_text(f"❌ حدث خطأ: {error_text[:100]}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
