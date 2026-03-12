import os
import asyncio
import time
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# إعدادات البوت الخاصة بك
API_ID = "21689125"  # ضع هنا الـ API ID الخاص بك (أرقام فقط)
API_HASH = "762c2f829871783067756e2936274e1d"  # ضع هنا الـ API HASH الخاص بك
BOT_TOKEN = "8701664697:AAEuxlF3u933KIB3DNouLE7E5_Y1_1hzn4A"

app = Client("KareemAutoBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def humanbytes(size):
    if not size: return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024: return f"{size:.2f} {unit}"
        size /= 1024

@app.on_message(filters.regex(r'http'))
async def download_video(client, message):
    url = message.text
    # رسالة ترحيبية بشكل احترافي
    status_msg = await message.reply_text("✨ **مرحباً بك في كريم أوتوبوت**\n\n🔍 جاري فحص الرابط ومعالجة الطلب...", quote=True)
    
    ydl_opts = {
        'format': 'best',
        'cookiefile': 'cookies.txt',  # تأكد من رفع ملف cookies.txt في السيرفر
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # شكل حركي بسيط
            await status_msg.edit_text("⏳ **بدأ التحميل الآن...**\n⚙️ يتم سحب الفيديو بأفضل جودة وصوت")
            
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text("🚀 **اكتمل التحميل!**\n📤 جاري رفع الفيديو إليك الآن...")
        
        await message.reply_video(
            video=filename,
            caption=f"✅ **تم التحميل بواسطة كريم أوتوبوت**\n\n🎬 **العنوان:** {info.get('title')}\n📦 **الحجم:** {humanbytes(os.path.getsize(filename))}",
            supports_streaming=True
        )
        
        await status_msg.delete()
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        error_text = str(e)
        if "Sign in to confirm you’re not a bot" in error_text:
            await status_msg.edit_text("❌ **فشل التحميل**\nيوتيوب يطلب ملف كوكيز (Cookies). يرجى رفع ملف `cookies.txt` بجانب الكود.")
        else:
            await status_msg.edit_text(f"❌ **حدث خطأ غير متوقع:**\n`{error_text[:100]}`")

print("كريم أوتوبوت يعمل الآن...")
app.run()
