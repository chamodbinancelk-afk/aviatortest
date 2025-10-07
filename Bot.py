import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from telegram import Bot
import time

BOT_TOKEN = '8299929776:AAGKU7rkfakmDBXdgiGSWzAHPgLRJs-twZg'
CHAT_ID = '-1003177936060'
FF_URL = 'https://www.forexfactory.com/calendar'

bot = Bot(token=BOT_TOKEN)
translator = Translator()
last_headline = None

def fetch_latest_news():
    global last_headline

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(FF_URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    event_cell = soup.find('td', class_='calendar__event-title')
    if not event_cell:
        return

    headline = event_cell.get_text(strip=True)
    if headline == last_headline:
        return
    last_headline = headline

    translation = translator.translate(headline, dest='si').text
    message = f"""🗞 ForexFactory News Update

English: {headline}
සිංහල: {translation}
"""

    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == '__main__':
    while True:
        try:
            fetch_latest_news()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(300)
