from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

Bot Token
BOT_TOKEN = "8299929776:AAGKU7rkfakmDBXdgiGSWzAHPgLRJs-twZg"

Start command handler
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    name = user.first_name or "friend"
    welcome_text = f"👋 හෙලෝ {name}! Welcome to the group/bot! 😊"
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)

Main bot setup
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if _name_ == "_main_":
    main()


