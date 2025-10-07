import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from telegram import Bot
import time

# Telegram Config
TELEGRAM_BOT_TOKEN = '8299929776:AAGKU7rkfakmDBXdgiGSWzAHPgLRJs-twZg'
TELEGRAM_CHAT_ID = '-1003177936060'

# ForexFactory News Page URL
FF_URL = 'https://www.forexfactory.com/news'

# Bot & Translator Init
bot = Bot(token=TELEGRAM_BOT_TOKEN)
translator = Translator()
last_headline = None

def fetch_latest_news():
    global last_headline

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(FF_URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the latest news block
    latest_news = soup.find('a', class_='title')

    if not latest_news:
        print("News not found!")
        return

    headline = latest_news.get_text(strip=True)

    # Prevent duplicate messages
    if headline == last_headline:
        return

    last_headline = headline

    # Translate
    translation = translator.translate(headline, dest='si').text

    message = f"""🗞 ForexFactory News Update
English: {headline}
සිංහල: {translation}
"""

    # Send to Telegram
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')

# Looping
if __name__ == '__main__':
    while True:
        try:
            fetch_latest_news()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(300)  # Every 5 min

