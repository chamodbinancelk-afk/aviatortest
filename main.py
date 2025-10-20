import telegram
import time
import pandas as pd
import random
from collections import deque
import requests # Live Data Fetching සඳහා අලුතින් එක් කරන ලදි
from bs4 import BeautifulSoup # Live Data Fetching සඳහා අලුතින් එක් කරන ලදි

# --- ⚠️ ඔබ විසින් වෙනස් කළ යුතු කොටස ---

# BotFather ගෙන් ලබාගත් ඔබගේ Token එක
BOT_TOKEN = '8382727460:AAEgKVISJN5TTuV4O-82sMGQDG3khwjiKR8' 

# ඔබගේ Channel එකේ Username හෝ Chat ID එක
# (උදා: @MySignalChannel, නැතිනම් -123456789 වැනි අංකයක්)
CHANNEL_ID = '-1003111341307' 

# -------------------------------------


# --- 1. Live Data ලබා ගැනීමේ ශ්‍රිතය (Web Scraping Logic) ---

def get_latest_crash_data(num_rounds=10):
    """
    Aviator ක්‍රීඩාවේ පසුගිය ප්‍රතිඵල (Multipliers) ලබා ගැනීමට උත්සාහ කරයි.
    මෙය HTML Scraping මත පදනම් වූවකි.
    """
    
    # ඔබගේ තිර රූවේ ඇති URL එක
    TARGET_URL = 'https://lk.1xbet.com/en/casino-search?game=52358' 
    
    headers = {
        # Browser එකක් ලෙස පෙනී සිටීම සඳහා (වෙබ් අඩවි මඟින් බොට්ලාව Block කිරීම වැලැක්වීමට)
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # සටහන: බොහෝ Aviator සයිට් වල දත්ත Load වන්නේ JavaScript මඟින් නිසා, 
        # සරල requests.get() අසාර්ථක විය හැක.
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        response.raise_for_status() 

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ⚠️ HTML Class නාමය ඉතා නිවැරදිව පරීක්ෂා කරන්න. 
        # මෙය ඔබගේ තිර රූවේ තිබූ නමකි. එය වෙනස් වී තිබිය හැක.
        # සජීවී දත්ත ලබාදෙන API එකක් සොයා ගැනීම වඩා හොඳය.
        multiplier_elements = soup.find_all('div', class_='payout-ng-star-inserted') 
        
        crash_results = []
        for element in multiplier_elements:
            try:
                # 'x' ලකුණ ඉවත් කර float අගයක් ලෙස ලබා ගැනීම
                multiplier_text = element.text.strip().replace('x', '')
                multiplier_value = float(multiplier_text)
                crash_results.append(multiplier_value)
            except ValueError:
                continue 
        
        # වඩාත් පැරණි ප්‍රතිඵල මුලින්ම එන නිසා, නවතම ඒවා අගින් තිබීමට ඉඩ ඇත.
        # අපි ලැයිස්තුව ආපසු හරවා, නවතම ඒවා මුලට ගන්නෙමු.
        return crash_results[::-1][:num_rounds]
        
    except requests.exceptions.RequestException as e:
        print(f"[{time.strftime('%H:%M:%S')}] ERROR: Live data fetching failed (Check URL/Network): {e}")
        return []


# --- 2. Martingale උපාය මාර්ගය විශ්ලේෂණය කිරීම ---

def analyze_and_generate_signal(historical_data, cashout_target=2.00):
    """
    ඓතිහාසික දත්ත විශ්ලේෂණය කර Martingale සිග්නලය තීරණය කරයි.
    """
    if not historical_data:
        return None, 0

    # අඛණ්ඩව ඉලක්කය අහිමි වූ වාර ගණන ගණනය කිරීම
    consecutive_losses = 0
    # නවතම ප්‍රතිඵලය මුලින්ම එන බැවින්, අපි ලැයිස්තුව දිගේ ඉදිරියට යමු.
    for multiplier in historical_data:
        if multiplier < cashout_target:
            consecutive_losses += 1
        else:
            break
            
    if consecutive_losses >= 3:
        # අඛණ්ඩව පාඩු 3ක් හෝ ඊට වැඩි ප්‍රමාණයක් සිදුවී ඇත්නම්, Martingale සිග්නලය නිකුත් කරයි.
        
        # Martingale ඔට්ටු ඒකකය: 2^(පාඩු වාර ගණන - 1)
        # උදා: 3 පාඩු = 4X ඔට්ටු ඒකකය (1, 2, 4)
        bet_multiplier = 2**(consecutive_losses - 1) 
        
        signal_text = (
            f"❌ අඛණ්ඩ පාඩු: {consecutive_losses} වතාවක් ({cashout_target}X ට අඩුවෙන්)\n"
            f"🎯 ඉලක්කය: {cashout_target}X\n"
            f"💰 ඊළඟ ඔට්ටුව: {bet_multiplier}X (පදනම් ඒකකයෙන්)"
        )
        return signal_text, bet_multiplier

    return None, 0 # සිග්නල් එකක් නොමැත


# --- 3. ටෙලිග්‍රෑම් පණිවිඩ යැවීමේ කාර්යය ---

def send_telegram_message(bot_token, chat_id, message):
    """
    ටෙලිග්‍රෑම් API හරහා පණිවිඩයක් යවයි.
    """
    try:
        bot = telegram.Bot(token=bot_token)
        bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
    except telegram.error.Unauthorized:
        print("ERROR: Invalid Bot Token or Chat ID.")
    except Exception as e:
        print(f"ERROR sending Telegram message: {e}")


# --- 4. ප්‍රධාන ක්‍රියාත්මක කිරීමේ ශ්‍රිතය ---

def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("ERROR: කරුණාකර BOT_TOKEN සහ CHANNEL_ID නිවැරදිව සකසන්න.")
        return

    # පසුගිය වට 50 ක ප්‍රතිඵල ගබඩා කිරීමට
    historical_data = deque(maxlen=50) 
    CASH_OUT_TARGET = 2.00 # Martingale Target Multiplier
    
    print("Live Data Signal Bot Started...")
    print(f"Target Cashout Multiplier: {CASH_OUT_TARGET}X")
    
    # අවසන් වරට පරීක්ෂා කළ ප්‍රතිඵලය මතක තබා ගැනීමට (දත්ත නැවත නැවත යැවීම වැලැක්වීමට)
    last_fetched_round = None 
    
    while True:
        try:
            # 1. සජීවී දත්ත ලබා ගැනීම
            # අපි දැනට පවතින දත්ත සියල්ල ලබා ගනිමු
            latest_results = get_latest_crash_data(num_rounds=15)
            
            if not latest_results:
                print(f"[{time.strftime('%H:%M:%S')}] No new data fetched. Retrying...")
                time.sleep(10)
                continue
            
            # 2. නව දත්ත පමණක් හසුරුවා ගැනීම
            # අපි දත්ත ලබාගැනීමේ ක්‍රමය වෙනස් කළ නිසා, historical_data එක update කරන්න.
            if last_fetched_round != latest_results[0]: # අලුත්ම ප්‍රතිඵලය වෙනස් වී ඇත්නම්
                
                # සම්පූර්ණ දත්ත ලැයිස්තුව update කිරීම
                historical_data.clear()
                historical_data.extend(latest_results)
                last_fetched_round = latest_results[0]
                current_multiplier = latest_results[0]
                
                # 3. තත්ත්ව වාර්තාව
                is_win = "✅ WIN" if current_multiplier >= CASH_OUT_TARGET else "❌ LOSS"
                print(f"[{time.strftime('%H:%M:%S')}] New Round: {current_multiplier}X - {is_win}")
                
                # 4. සිග්නල් විශ්ලේෂණය
                # historical_data හි නවතම ප්‍රතිඵලය මුලින්ම ඇත
                signal_message, bet_multiplier = analyze_and_generate_signal(historical_data, CASH_OUT_TARGET)
                
                # 5. සිග්නලය යැවීම
                if signal_message:
                    full_message = (
                        f"🚨 *MARTINGALE SIGNAL* 🚨\n\n"
                        f"{signal_message}\n\n"
                        f"_වගකීමෙන් යුතුව ඔට්ටු අල්ලන්න_"
                    )
                    send_telegram_message(BOT_TOKEN, CHANNEL_ID, full_message)
                
            else:
                print(f"[{time.strftime('%H:%M:%S')}] No new rounds detected.")


            # 6. ඊළඟ වටය සඳහා රැඳී සිටීම
            time.sleep(10) 

        except Exception as e:
            print(f"A critical error occurred: {e}")
            time.sleep(30) # දෝෂයක් ඇති වුවහොත් 30s විරාමයක්

if __name__ == '__main__':
    main()
