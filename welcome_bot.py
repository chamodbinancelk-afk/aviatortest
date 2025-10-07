from telegram.ext import Updater, CommandHandler
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Start command handler
def start(update, context):
    welcome_message = """👋 **Welcome to the C F Sinhala News Bot** 🇱🇰

📈 You'll receive real-time news updates from *Fundamental News* translated into *Sinhala* directly to C F NEWS Telegram channel.

💡 Stay informed. Trade smart. Good luck

📢 **News updates will be posted automatically**
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message, parse_mode='Markdown')

# Main function
def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
