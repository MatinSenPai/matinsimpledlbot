import logging
import requests
import os
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace 'YOUR_BOT_API_TOKEN' with your actual bot token
TOKEN = '7167126167:AAG-N7X-fpgHpr0yFTsH4Eez5ViAIaYzZCM'

# Function to download a file from a given URL
def download_file(url: str) -> str:
    local_filename = url.split('/')[-1]
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # Ensure we notice bad responses
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except requests.RequestException as e:
        logger.error(f"Error downloading file: {e}")
        return None
    return local_filename

# Handler for the /start command
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf'Hi {user.mention_html()}! Send me a direct file link, and I will download the file and send it back to you.',
        reply_markup=ForceReply(selective=True),
    )

# Handler for messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    if not url.startswith("http"):
        await update.message.reply_text("Please send a valid URL.")
        return
    
    try:
        await update.message.reply_text('Downloading the file...')
        file_path = download_file(url)
        if file_path:
            with open(file_path, 'rb') as f:
                await context.bot.send_document(chat_id=update.effective_chat.id, document=f)
            os.remove(file_path)  # Clean up the downloaded file
        else:
            await update.message.reply_text("Failed to download the file. Please check the URL and try again.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"Failed to handle the file. Error: {e}")

# Main function to start the bot
if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print('Polling........')
    application.run_polling(poll_interval=3)
