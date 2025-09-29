import requests
from bs4 import BeautifulSoup
from telegram import Bot
from googletrans import Translator
import time
import os

# --- 1. Settings (සැකසීම්) ---

# Telegram Bot Token එක සහ Channel ID එක
TELEGRAM_BOT_TOKEN = "8299929776:AAGKU7rkfakmDBXdgiGSWzAHPgLRJs-twZg" # BotFather වෙතින් ලබා ගන්න
TELEGRAM_CHANNEL_ID = "-1003177936060" # නාලිකාවේ ID එක

# Google Cloud Translation සඳහා අවශ්‍ය පරිසර විචල්‍යය (Authentication)
# 'google-cloud-translate' පුස්තකාලය භාවිතා කිරීමට ඔබගේ පරිසරයේ Google Cloud Credentials සකස් කර තිබිය යුතුය.
# උදා: os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/your/service-account-file.json"

# MyFXBook Economic Calendar URL එක
MYFXBOOK_URL = "https://www.myfxbook.com/forex-economic-calendar"

# --- 2. Functions (ක්‍රියාකාරීත්වය) ---

def get_latest_news():
    """
    MyFXBook වෙතින් නවතම ප්‍රවෘත්ති දත්ත ලබා ගැනීම.
    මෙය සරල Web Scraping උදාහරණයකි.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(MYFXBOOK_URL, headers=headers, timeout=10)
        response.raise_for_status() # දෝෂ ඇත්නම් exception එකක් නිකුත් කරයි

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # MyFXBook හි දත්ත වගුව සොයා ගැනීම. නිශ්චිත ID/Class එකක් අවශ්‍යයි.
        # මෙහි උදාහරණයක් ලෙස 'calendar-table' නම් Class එකක් යොදා ඇත.
        news_table = soup.find('table', {'id': 'calendarTable'}) 
        
        if news_table:
            # නවතම පුවත් පේළි කිහිපයක් පමණක් ලබා ගැනීමට උත්සාහ කිරීම
            news_rows = news_table.find_all('tr', class_='calendar_row')[:5] 
            
            news_data = []
            for row in news_rows:
                # දත්ත ලබා ගන්නා ආකාරය ඔබ MyFXBook හි ව්‍යුහය අනුව වෙනස් කළ යුතුය.
                time_val = row.find('td', class_='time').text.strip() if row.find('td', class_='time') else 'N/A'
                currency = row.find('td', class_='currency').text.strip() if row.find('td', class_='currency') else 'N/A'
                event = row.find('td', class_='event').text.strip() if row.find('td', class_='event') else 'N/A'
                
                # වැදගත්කම (Impact) සලකුණු කර ගන්න. (High/Medium)
                impact = "High Impact" # සැබෑ Scraping Logic එක මෙහි ඇතුළත් කළ යුතුය
                
                news_data.append({
                    'time': time_val,
                    'currency': currency,
                    'event_en': event,
                    'impact': impact
                })
            return news_data
        
        return []

    except requests.RequestException as e:
        print(f"Error fetching data from MyFXBook: {e}")
        return []

def translate_to_sinhala(text_en):
    """
    Google Cloud Translation API භාවිතයෙන් ඉංග්‍රීසි සිංහලට පරිවර්තනය කිරීම.
    """
    try:
        translate_client = translate.Client()
        result = translate_client.translate(
            text_en,
            target_language='si' # සිංහල භාෂා කේතය
        )
        return result['translatedText']
    except Exception as e:
        print(f"Translation Error: {e}")
        return f"පරිවර්තනය අසාර්ථකයි: {text_en}"

def send_telegram_message(message):
    """
    ටෙලිග්‍රෑම් නාලිකාවට පණිවිඩයක් යැවීම.
    """
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=message,
            parse_mode='Markdown' # පණිවිඩය හැඩ ගැන්වීමට
        )
        print("Telegram message sent successfully.")
    except Exception as e:
        print(f"Telegram Error: {e}")

def main_job():
    """
    ප්‍රධාන ක්‍රියාවලිය
    """
    print(f"Starting job at {time.ctime()}")
    
    # 1. දත්ත ලබා ගැනීම
    news_items = get_latest_news()

    if not news_items:
        print("No new news items found or error in scraping.")
        return

    message_parts = []

    for item in news_items:
        # 2. පරිවර්තනය
        event_si = translate_to_sinhala(item['event_en'])
        
        # 3. පණිවිඩය සකස් කිරීම
        telegram_message = (
            f"🚀 *මූලික පුවත් නිකුත් කිරීම!*\n"
            f"--------------------------------\n"
            f"🕰️ *වේලාව (Time):* {item['time']}\n"
            f"💱 *මුදල් ඒකකය (Currency):* {item['currency']}\n"
            f"🔥 *වැදගත්කම (Impact):* {item['impact']}\n"
            f"📰 *පුවත (Event):* {event_si}\n"
            f"--------------------------------\n"
        )
        message_parts.append(telegram_message)

    # සියලු පුවත් එකම පණිවිඩයකට එකතු කර යැවීම (වෙන වෙනම යැවීමටද පුළුවන්)
    final_message = "\n".join(message_parts)
    
    # 4. ටෙලිග්‍රෑම් වෙත යැවීම
    send_telegram_message(final_message)
    
    print(f"Job finished at {time.ctime()}")

# --- 3. Run the Job (ක්‍රියාත්මක කිරීම) ---

if __name__ == "__main__":
    while True:
      main_job()
      time.sleep(100)
    # මෙම කේතය ස්වයංක්‍රීයව ක්‍රියාත්මක වීමට සකසන්න (උදා: සෑම විනාඩි 5 කට වරක්)
    # Production Level එකකදී, Cron Job හෝ Cloud Scheduler එකක් භාවිතා කරන්න.
    
    # උදාහරණයක් ලෙස විනාඩි 5ක් (තත්පර 300) යනතුරු නිරන්තරයෙන් ක්‍රියාත්මක වීමට
    # while True:
    #     main_job()
    #     time.sleep(300) # තත්පර 300 ක් නවතී
    
    # වරක් පමණක් ක්‍රියාත්මක කර බැලීමට
