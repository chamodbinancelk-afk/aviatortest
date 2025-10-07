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
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL_SEC", 1))
LAST_HEADLINE_FILE = "last_headline.txt"

bot = Bot(token=BOT_TOKEN)
translator = Translator()

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

    latest = soup.find('a', class_='title')
    if not latest:
        logging.warning("News title not found.")
        return

    headline = latest.get_text(strip=True)
    if headline == last:
        return

    write_last_headline(headline)

    # Translate
    try:
        translation = translator.translate(headline, dest='si').text
    except Exception as e:
        translation = "සිංහල පරිවර්තනය ලබාගැනීමට නොහැක."
        logging.error(f"Translation error: {e}")

    # Date and time
    now = datetime.now()
    date_time = now.strftime('%Y-%m-%d %I:%M %p')

    # Try to get an image from the article if available
    image_url = None
    article_link = "https://www.forexfactory.com" + latest['href']
    try:
        article_page = requests.get(article_link, headers=headers)
        article_soup = BeautifulSoup(article_page.content, 'html.parser')
        img = article_soup.find('img')
        if img and 'src' in img.attrs:
            image_url = img['src']
    except Exception as e:
        logging.warning("Image fetch failed.")

    # Message format
    caption = f"""📰 **Fundamental News (සිංහල)**

🕒 **Date & Time:** {date_time}


**English:** {headline}


**සිංහල:** {translation}


🔗 [Read More]({article_link})


🚀 **Dev :** Mr Chamo 🇱🇰
"""

    if image_url:
        bot.send_photo(chat_id=CHAT_ID, photo=image_url, caption=caption, parse_mode='Markdown')
    else:
        bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode='Markdown')

    logging.info("News sent: %s", headline)

if __name__ == '__main__':
    while True:
        try:
            fetch_latest_news()
        except Exception as e:
            logging.error(f"Loop error: {e}")
        time.sleep(FETCH_INTERVAL)


