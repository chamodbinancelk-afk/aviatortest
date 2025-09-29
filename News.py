from googletrans import Translator
from telegram import Bot

def translate_and_send(news_en):
    # 🔁 Initialize translator
    translator = Translator()
    
    # 🌐 Translate English news to Sinhala
    translated = translator.translate(news_en, dest='si').text

    # 📲 Telegram Bot Config
    TELEGRAM_BOT_TOKEN = '8299929776:AAGKU7rkfakmDBXdgiGSWzAHPgLRJs-twZg'
    TELEGRAM_CHAT_ID = '-1003177936060'  # Use -100... for channels

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # 📨 Send message
    message = f"📰 *Fundamental News (සිංහල)*\ntranslated"
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")

if _name_ == "_main_":
    # 📰 Example news input (replace with real-time API or data)
    sample_news = "US Federal Reserve expected to cut interest rates today, increasing market volatility."
    translate_and_send(sample_news)
