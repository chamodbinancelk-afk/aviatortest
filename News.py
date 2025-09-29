import requests
import time
from telegram import Bot
from bs4 import BeautifulSoup

Config
TELEGRAM_TOKEN = "8299929776:AAGKU7rkfakmDBXdgiGSWzAHPgLRJs-twZg"
CHAT_ID = "-1003177936060"
DEEPL_API_KEY = "YOUR_DEEPL_API_KEY"
RSS_FEED_URL = "https://www.myfxbook.com/news/rss"  # Example URL, change to real feed

def translate_text(text, target_lang="SI"):
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "target_lang": target_lang
    }
    resp = requests.post(url, data=params)
    result = resp.json()
    return result["translations"][0]["text"]

def fetch_latest_news():
    resp = requests.get(RSS_FEED_URL)
    soup = BeautifulSoup(resp.content, features="xml")
    items = soup.findAll("item")
    news = []
    for item in items:
        title = item.title.text
        link = item.link.text
        news.append((title, link))
    return news

def main():
    posted = set()
    while True:
        news_list = fetch_latest_news()
        for title, link in news_list:
            if link not in posted:
                translated = translate_text(title + "\n" + link)
                bot.send_message(chat_id=CHAT_ID, text=translated)
                posted.add(link)
        time.sleep(300)  # every 5 minutes

if _name_ == "_main_":
    main()
