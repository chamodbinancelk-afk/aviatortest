import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8299929776:AAGKU7rkfakmDBXdgiGSWzAHPgLRJs-twZg"  # 👉 ඔයාගෙ token එක මෙතන දාන්න

Start command function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "friend"
    welcome_text = f"👋 හෙලෝ {name}! Welcome to the group/bot! 😊"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)

Main function
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("🤖 Bot is running...")
    await app.run_polling()

Run the bot
if _name_ == "_main_":
    asyncio.run(main())

