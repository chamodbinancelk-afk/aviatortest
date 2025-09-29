import requests
import time
from bs4 import BeautifulSoup
from googletrans import Translator
from telegram import Bot

RSS_URL = "https://www.myfxbook.com/rss"  # or news-specific feed
CHECK_INTERVAL = 100  # seconds

BOT_TOKEN = "8299929776:AAGKU7rkfakmDBXdgiGSWzAHPgLRJs-twZg"
CHAT_ID = "-1003177936060"
translator = Translator()

bot = Bot(token=BOT_TOKEN)

posted = set()

def fetch_news_items():
    resp = requests.get(RSS_URL)
    soup = BeautifulSoup(resp.content, "xml")
    items = soup.find_all("item")
    results = []
    for it in items:
        title = it.title.text
        link = it.link.text
        results.append((title, link))
    return results

def translate_text(text, target="si"):
    try:
        return translator.translate(text, dest=target).text
    except Exception as e:
        print("Translate error:", e)
        return text

def send_news():
    global posted
    items = fetch_news_items()
    for title, link in items:
        if link not in posted:
            translated = translate_text(title + "\n" + link)
            msg = f"📰 Fundamental News (සිංහල)\ntranslated"
            bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
            posted.add(link)

if name == "main":
    while True:
        send_news()
        time.sleep(CHECK_INTERVAL)
