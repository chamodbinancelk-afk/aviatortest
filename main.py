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
# Changed interval to a safer 300 seconds (5 minutes) to avoid IP blocking
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL_SEC", 300)) 

# File path definitions
LAST_FF_HEADLINE_FILE = "last_ff_headline.txt"
LAST_CNBC_HEADLINE_FILE = "last_cnbc_headline.txt"

# --- Initialization and Stability Check ---
if not BOT_TOKEN or not CHAT_ID:
    print("CRITICAL ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing or not loaded.")
    exit()

try:
    # Use a stable service URL for googletrans
    translator = Translator(service_urls=['translate.googleapis.com']) 
    bot = Bot(token=BOT_TOKEN)
    # Attempt a simple check to confirm connection (optional, but good practice)
    # print(f"Bot connected successfully. User ID: {bot.get_me().id}")
except Exception as e:
    print(f"CRITICAL ERROR: Bot initialization failed. Check your token/internet connection. Error: {e}")
    exit()

# Setup logging (logs to file and console)
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s: %(message)s',
                    handlers=[
                        logging.FileHandler("bot.log", encoding='utf-8'),
                        logging.StreamHandler() # Output to console
                    ])


# --- File I/O Functions ---

def read_last_headline(filename):
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        logging.error(f"Error reading file {filename}: {e}")
        return None

def write_last_headline(filename, headline):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(headline)
    except Exception as e:
        logging.error(f"Error writing to file {filename}: {e}")

# --- News Fetching Functions (Added/Completed) ---

def fetch_forexfactory_news():
    """Forex Factory වෙතින් නවතම ප්‍රවෘත්ති සොයයි."""
    logging.info("Fetching Forex Factory news...")
    try:
        resp = requests.get(FF_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # FF හි නවතම පුවත සොයයි (news__item--time class එක භාවිත කරයි)
        latest_story = soup.find('div', class_=lambda c: c and 'news__item' in c) 
        
        if latest_story:
            link_tag = latest_story.find('a', class_='news__item-title')
            
            if link_tag and 'href' in link_tag.attrs:
                headline = link_tag.get_text(strip=True)
                news_url = "https://www.forexfactory.com" + link_tag['href']
                
                return headline, news_url, None
        
        logging.info("FF: No new headline found on the page.")
        return None, None, None
    except Exception as e:
        logging.error(f"FF Fetching Error: {e}")
        return None, None, None

def fetch_cnbc_news():
    """CNBC වෙතින් නවතම ප්‍රවෘත්ති සොයයි."""
    CNBC_URL = "https://www.cnbc.com/world/?region=world" 
    logging.info("Fetching CNBC news...")
    try:
        resp = requests.get(CNBC_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # CNBC හි ප්‍රවෘත්ති ලැයිස්තුව සොයයි (LatestNews-list class එක)
        latest_list = soup.find('div', class_='LatestNews-list')
        
        if latest_list:
            # ලැයිස්තුවේ ඇති පළමු ප්‍රවෘත්ති සබැඳිය සොයයි
            latest_item = latest_list.find('div', class_='LatestNews-listEntry')
            link_tag = latest_item.find('a') if latest_item else None
            
            if link_tag and 'href' in link_tag.attrs:
                headline = link_tag.get_text(strip=True)
                news_url = link_tag['href']
                
                # රූපය සොයා ගැනීමට උත්සාහ කරයි
                img_tag = latest_item.find('img') if latest_item else None
                img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None
                
                return headline, news_url, img_url
        
        logging.info("CNBC: No new headline found on the page.")
        return None, None, None
    except Exception as e:
        logging.error(f"CNBC Fetching Error: {e}")
        return None, None, None

# --- Send Telegram Function (with all previous fixes) ---
def send_telegram_news(headline, news_url, img_url, source):
    logging.info(f"Attempting to process news: {headline[:50]}...")
    try:
        # 1. Description Fetching
        news_resp = requests.get(news_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        news_resp.raise_for_status()
        news_soup = BeautifulSoup(news_resp.content, 'html.parser')
        
        description = "No description found."
        desc_tag = None

        if source == "Forex Factory":
            desc_tag = news_soup.find('p', class_='news__copy')
        elif source == "CNBC":
            # CNBC වැනි අනෙකුත් වෙබ් අඩවි සඳහා නම්‍යශීලී සෙවීම
            desc_tag = news_soup.find('p') or news_soup.find('div', class_=lambda c: c and 'article-content' in c)

        if desc_tag:
            description = desc_tag.get_text(strip=True).replace('\n', ' ')[:500].strip()
        
    except Exception as e:
        logging.error(f"Failed to fetch or parse description for {source} at {news_url}: {e}")
        description = "No description found. (විස්තරය ලබා ගැනීමේ දෝෂයක්)"


    # 2. Translation (with robust error handling)
    description_si = "සිංහල පරිවර්තනය අසාර්ථක විය." 

    if description and description != "No description found." and "No description found. (" not in description:
        try:
            translation_result = translator.translate(description, dest='si')
            description_si = translation_result.text
            time.sleep(1) # googletrans සීමා වීම් මග හරවා ගැනීමට
            
        except Exception as e:
            logging.error(f"Translation failed for news from {source}. Error: {e}")
            description_si = f"සිංහල පරිවර්තනය අසාර්ථක විය. (දෝෂය: {str(e)[:40]}...)"


    # 3. Message Formatting
    sri_lanka_tz = pytz.timezone('Asia/Colombo')
    now = datetime.now(sri_lanka_tz)
    date_time = now.strftime('%Y-%m-%d %I:%M %p')

    message = f"""📰 *Fundamental News (සිංහල)*

⏰ *Date & Time:* {date_time}
🌍 *Source:* {source}

🧠 *Headline:* {headline}

🔥 *සිංහල:* {description_si}

🔗 *Read more:* {news_url}

🚀 *Dev : Mr Chamo 🇱🇰*
"""

    # 4. Sending to Telegram
    try:
        if img_url:
            bot.send_photo(chat_id=CHAT_ID, photo=img_url, caption=message, parse_mode='Markdown')
        else:
            bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        logging.info(f"SUCCESS: Posted news from {source}: {headline}")
    except Exception as e:
        logging.error(f"FAILED to send message to Telegram. Check CHAT_ID or BOT_TOKEN permissions. Error: {e}")

# --- Main Loop ---
if __name__ == "__main__":
    logging.info("Forex News Bot Started.")
    print("Forex News Bot is running. Check 'bot.log' for details.")
    print(f"Fetching every {FETCH_INTERVAL} seconds. (Adjust FETCH_INTERVAL_SEC in .env if needed)")

    while True:
        
        # 1. ForexFactory news check
        print("\n--- Checking Forex Factory ---")
        last_ff = read_last_headline(LAST_FF_HEADLINE_FILE)
        ff_headline, ff_url, ff_img = fetch_forexfactory_news()
        
        if ff_headline and ff_headline != last_ff:
            send_telegram_news(ff_headline, ff_url, ff_img, "Forex Factory")
            write_last_headline(LAST_FF_HEADLINE_FILE, ff_headline) 
        elif ff_headline:
             print(f"FF: Headline found but already posted: {ff_headline[:50]}...")
        else:
             print("FF: No new or valid headline found.")

        # 2. CNBC news check
        print("--- Checking CNBC ---")
        last_cnbc = read_last_headline(LAST_CNBC_HEADLINE_FILE)
        cnbc_headline, cnbc_url, cnbc_img = fetch_cnbc_news()
        
        if cnbc_headline and cnbc_headline != last_cnbc:
            send_telegram_news(cnbc_headline, cnbc_url, cnbc_img, "CNBC")
            write_last_headline(LAST_CNBC_HEADLINE_FILE, cnbc_headline)
        elif cnbc_headline:
            print(f"CNBC: Headline found but already posted: {cnbc_headline[:50]}...")
        else:
            print("CNBC: No new or valid headline found.")

        print(f"Sleeping for {FETCH_INTERVAL} seconds...")
        time.sleep(FETCH_INTERVAL)
