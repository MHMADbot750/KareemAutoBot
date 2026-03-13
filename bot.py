import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ChatAction

TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

def ytdl_download(url, filename, fmt):
    opts = {
        # 'best' تختار أفضل جودة فيديو وصوت مدمجة مباشرة لتجنب مشاكل الدمج
        "format": "best[ext=mp4]/best", 
        "outtmpl": filename,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "addmetadata": True,
        "geo_bypass": True,
        "source_address": "0.0.0.0", # يساعد في تخطي بعض القيود
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً كريم! أرسل رابط الفيديو وسأحاول تحميله بأقصى سرعة.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "http" in url:
        keyboard = [[InlineKeyboardButton("ابدأ التحميل الآن 📥", callback_data=f"dl|best|{url}")]]
        await update.message.reply_text("تم استلام الرابط، اضغط للبدء:", reply_markup=InlineKeyboardMarkup(keyboard))

async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, fmt, url = query.data.split("|")
    
    msg = await query.message.reply_text("⏳ جاري سحب الفيديو من السيرفر... انتظر قليلاً.")
    filename = f"vid_{query.from_user.id}.mp4"

    try:
        await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.UPLOAD_VIDEO)
        
        # تشغيل التحميل
        await asyncio.to_thread(ytdl_download, url, filename, fmt)
        
        if os.path.exists(filename):
            with open(filename, "rb") as video_file:
                await query.message.reply_video(
                    video=video_file, 
                    caption="تم التحميل بنجاح ✅\nبواسطة @KareemAutoBot",
                    write_timeout=1000 # وقت طويل جداً للرفع
                )
            os.remove(filename)
            await msg.delete()
        else:
            await msg.edit_text("❌ يوتيوب منع السيرفر من التحميل حالياً، جرب رابطاً آخر أو انتظر قليلاً.")
    except Exception as e:
        await msg.edit_text(f"❌ خطأ تقني: {str(e)[:100]}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(download_callback, pattern="^dl"))
    app.run_polling()

if __name__ == "__main__":
    main()
