import os
import requests
import tempfile
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8702189777:AAEanAPGKaubVcD4nr1Hv8hCvlojD9uUGWI')
HF_SPACE_URL = os.environ.get('HF_SPACE_URL', 'https://kokow457-myanmar-dubber.hf.space')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = update.message.chat_id
    
    if not text.startswith(('http://', 'https://')):
        await context.bot.send_message(
            chat_id=chat_id,
            text="📎 ဒီ bot သုံးနည်း:\n\n"
                 "• YouTube link ပို့ပါ\n"
                 "• TikTok link ပို့ပါ\n"
                 "• Facebook link ပို့ပါ\n"
                 "• Video file တိုက်ရိုက် upload လုပ်ပါ\n\n"
                 "ဥပမာ: https://www.youtube.com/watch?v=xxxxx"
        )
        return
    
    await context.bot.send_message(chat_id=chat_id, text="🔄 Processing လုပ်နေတယ်... ခဏစောင့်ပါ (၁-၃ မိနစ်ခန့်)")
    
    try:
        response = requests.post(
            f"{HF_SPACE_URL}/api/telegram-dub",
            json={"url": text},
            timeout=600
        )
        
        if response.status_code == 200:
            tmp_output = tempfile.mktemp(suffix=".mp4")
            with open(tmp_output, 'wb') as f:
                f.write(response.content)
            
            await context.bot.send_message(chat_id=chat_id, text="✅ ပြီးပါပြီ! Video ပို့ပေးနေတယ်...")
            with open(tmp_output, 'rb') as f:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=f,
                    caption="🎬 Myanmar Dubbed Video",
                    supports_streaming=True
                )
            os.remove(tmp_output)
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
            except:
                error_msg = f'HTTP {response.status_code}'
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: {error_msg}")
            
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: {str(e)[:200]}")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    video = update.message.video or update.message.document
    
    if not video:
        await context.bot.send_message(chat_id=chat_id, text="❌ Video file မတွေ့ဘူး")
        return
    
    await context.bot.send_message(chat_id=chat_id, text="📥 Video ရပါပြီ။ Processing လုပ်နေတယ်...")
    
    try:
        file = await context.bot.get_file(video.file_id)
        tmp_input = tempfile.mktemp(suffix=".mp4")
        await file.download_to_drive(tmp_input)
        
        with open(tmp_input, 'rb') as f:
            response = requests.post(
                f"{HF_SPACE_URL}/api/telegram-dub",
                files={'file': f},
                timeout=600
            )
        
        os.remove(tmp_input)
        
        if response.status_code == 200:
            tmp_output = tempfile.mktemp(suffix=".mp4")
            with open(tmp_output, 'wb') as f:
                f.write(response.content)
            
            await context.bot.send_message(chat_id=chat_id, text="✅ ပြီးပါပြီ! Video ပို့ပေးနေတယ်...")
            with open(tmp_output, 'rb') as f:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=f,
                    caption="🎬 Myanmar Dubbed Video",
                    supports_streaming=True
                )
            os.remove(tmp_output)
        else:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: HTTP {response.status_code}")
            
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: {str(e)[:200]}")

def main():
    print("🤖 Starting Telegram Bot...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    print("✅ Bot is running! Send a YouTube link to your bot.")
    app.run_polling()

if __name__ == '__main__':
    main()
