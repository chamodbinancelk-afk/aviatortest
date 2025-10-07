import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from telegram import Bot
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FF_CALENDAR_URL = "https://www.forexfactory.com/calendar"
FETCH_INTERVAL = 1  # 5 minutes

bot = Bot(token=BOT_TOKEN)
translator = Translator()
sent_events = set()

def fetch_calendar_events():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(FF_CALENDAR_URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    rows = soup.select('tr.calendar__row')  # Select each event row
    for row in rows:
        time_cell = row.select_one('td.calendar__time')
        event_cell = row.select_one('td.calendar__event')
        impact_cell = row.select_one('td.calendar__impact span')
        country_cell = row.select_one('td.calendar__country')

        if not time_cell or not event_cell:
            continue

        event_time = time_cell.get_text(strip=True)
        event_name = event_cell.get_text(strip=True)
        impact = impact_cell.get('title', '') if impact_cell else 'Low'
        country = country_cell.get('title', '') if country_cell else 'Unknown'

        unique_id = f"{event_time}_{event_name}"
        if unique_id in sent_events:
            continue  # Avoid re-sending same event

        sent_events.add(unique_id)

        # Translate
        try:
            si_translation = translator.translate(event_name, dest='si').text
        except:
            si_translation = "සිංහල පරිවර්තනය නොහැක"

        now = datetime.now().strftime('%Y-%m-%d %I:%M %p')

        message = f"""📅 **Economic Calendar Event**

🕒 **Date/Time**: {now}

🌍 **Country**: {country}

⚠ **Impact**: {impact}

🔸 **Event**: {event_name}

🔸 **සිංහල**: {si_translation}


🚀 **Dev :** Mr Chamo 🇱🇰
"""

        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        time.sleep(2)  # avoid Telegram flood

if __name__ == '__main__':
    while True:
        try:
            fetch_calendar_events()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(FETCH_INTERVAL)
