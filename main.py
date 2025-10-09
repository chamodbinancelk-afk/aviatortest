import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv
import pytz
import os
import time
import logging

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FF_URL = os.getenv("FOREXFACTORY_NEWS_URL", "https://www.forexfactory.com/news")
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL_SEC", 1))
LAST_HEADLINE_FILE = "last_headline.txt"

bot = Bot(token=BOT_TOKEN)
translator = Translator()

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
    try:
        resp = requests.get(FF_URL, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to fetch news page: {e}")
        return

    soup = BeautifulSoup(resp.content, 'html.parser')

    news_link_tag = soup.find('a', href=lambda href: isinstance(href, str) and href.startswith('/news/') and not href.endswith('/hit'))
    if not news_link_tag:
        logging.warning("News element not found!")
        return

    headline = news_link_tag.get_text(strip=True)
    if headline == last:
        return

    write_last_headline(headline)

    news_url = "https://www.forexfactory.com" + news_link_tag['href']

    try:
        news_resp = requests.get(news_url, headers=headers, timeout=10)
        news_resp.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to fetch news detail page: {e}")
        return

    news_soup = BeautifulSoup(news_resp.content, 'html.parser')

    img_tag = news_soup.find('img', class_='attach')
    img_url = img_tag['src'] if img_tag else None

    desc_tag = news_soup.find('p', class_='news__copy')
    description = desc_tag.get_text(strip=True) if desc_tag else "No description found."

    try:
        headline_si = translator.translate(headline, dest='si').text
    except Exception as e:
        headline_si = "Translation failed"
        logging.error(f"Headline translation error: {e}")

    try:
        description_si = translator.translate(description, dest='si').text
    except Exception as e:
        description_si = "Description translation failed"
        logging.error(f"Description translation error: {e}")

    sri_lanka_tz = pytz.timezone('Asia/Colombo')
    now = datetime.now(sri_lanka_tz)
    date_time = now.strftime('%Y-%m-%d %I:%M %p')

    message = f"""📰 *Fundamental News (සිංහල)*
    

⏰ *Date & Time:* {date_time}

🌎 *Headline:* {headline}


🔥 *සිංහල:* {description_si}


🚀 *Dev :* Mr Chamo 🇱🇰
"""

    try:
        if img_url:
            bot.send_photo(chat_id=CHAT_ID, photo=img_url, caption=message, parse_mode='Markdown')
        else:
            bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        logging.info(f"Posted: {headline}")
    except Exception as e:
        logging.error(f"Failed to send message: {e}")

if __name__ == "__main__":
    while True:
        fetch_latest_news()
        time.sleep(FETCH_INTERVAL)
