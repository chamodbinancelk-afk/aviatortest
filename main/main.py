import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from telegram import Bot
from dotenv import load_dotenv
from datetime import datetime
import os
import time
import logging

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FF_URL = os.getenv("FOREXFACTORY_NEWS_URL", "https://www.forexfactory.com/news")
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL_SEC", 60))
LAST_HEADLINE_FILE = "last_headline.txt"

bot = Bot(token=BOT_TOKEN)
translator = Translator()
now = datetime.now() 
date_time = now.strftime('%Y-%m-%d %I:%M %p')

# Setup logging
logging.basicConfig(level=logging.INFO, filename="bot.log",
                    format='%(asctime)s %(levelname)s: %(message)s')

def read_last_headline():
    if not os.path.exists(LAST_HEADLINE_FILE):
        return None
    with open(LAST_HEADLINE_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()

def write_last_headline(headline):
    with open(LAST_HEADLINE_FILE, 'w', encoding='utf-8') as f:
        f.write(headline)

def fetch_latest_news():
    last = read_last_headline()
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(FF_URL, headers=headers, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, 'html.parser')

    latest = soup.find('h1')
    if not latest:
        logging.warning("News element not found!")
        return

    headline = latest.get_text(strip=True)
    if headline == last:
        return

    write_last_headline(headline)

    try:
        translation = translator.translate(headline, dest='si').text
    except Exception as e:
        translation = "Translation failed"
        logging.error(f"Translation error: {e}")

    message = f"""📰 *Fundamental News (සිංහල)*
    

⏰ *Date*: {date_time}


🌎 *English*: {headline}


🔥 *සිංහල*: {translation}


🚀 *Dev* : Mr Chamo 🇱🇰
"""

    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
    logging.info(f"Posted: {headline}")

if __name__ == '__main__':
    while True:
        try:
            fetch_latest_news()
        except Exception as e:
            logging.error(f"Error in loop: {e}")
        time.sleep(FETCH_INTERVAL)


