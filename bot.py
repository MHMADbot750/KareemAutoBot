import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ChatAction

# توكن البوت
TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

def ytdl_download(url, filename, fmt):
    opts = {
        "format": f"{fmt}+bestaudio/best/best",
        "outtmpl": filename,
        "quiet": True,
        "noplaylist": True,
        "merge_output_format": "mp4",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً كريم! أرسل رابط فيديو وسأقوم بتحميله لك.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url:
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)
            buttons = []
            # عرض الجودات المتوفرة
            for f in info.get("formats", []):
                h = f.get("height")
                if h in [360, 480, 720]:
                    buttons.append([InlineKeyboardButton(f"{h}p", callback_data=f"dl|{f['format_id']}|{url}")])
            
            if not buttons:
                buttons.append([InlineKeyboardButton("تحميل بأفضل جودة", callback_data=f"dl|best|{url}")])
                
            await update.message.reply_text("اختر الجودة المطلوبة:", reply_markup=InlineKeyboardMarkup(buttons[:8]))
        except Exception as e:
            await update.message.reply_text(f"خطأ في الرابط: {e}")

async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, fmt, url = query.data.split("|")
    
    msg = await query.message.reply_text("⏳ جاري التحميل والرفع... قد يستغرق ذلك دقائق للملفات الكبيرة.")
    filename = f"video_{query.from_user.id}.mp4"

    try:
        await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.UPLOAD_VIDEO)
        await asyncio.to_thread(ytdl_download, url, filename, fmt)
        
        if os.path.exists(filename):
            with open(filename, "rb") as video_file:
                await query.message.reply_video(
                    video=video_file, 
                    caption="تم التحميل بواسطة بوت كريم ✅",
                    write_timeout=600, # 10 دقائق للرفع
                    read_timeout=600
                )
            os.remove(filename)
            await msg.delete()
        else:
            await msg.edit_text("❌ فشل التحميل، حاول مرة أخرى.")
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(download_callback, pattern="^dl"))
    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
