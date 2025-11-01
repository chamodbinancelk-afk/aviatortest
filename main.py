import telegram
from telegram.ext import Updater, CommandHandler
import random
import logging

# වැදගත්: ඔබේ Bot Token එක මෙතැනට දාන්න
TELEGRAM_BOT_TOKEN = '8382727460:AAEgKVISJN5TTuV4O-82sMGQDG3khwjiKR8' 

# Log සකස් කිරීම
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Prediction Logic එක ---
# Wingo වල ප්‍රතිඵල අහඹු නිසා, මේක සරල අහඹු තේරීමක් හෝ සරල රටාවක් පමණයි.
# ඔබට මේ කොටස සංකීර්ණ රටා මත පදනම් වූ logic එකකින් වෙනස් කරන්න පුළුවන්.

def generate_prediction():
    # Colors: Red, Green, Violet
    colors = ['Green', 'Red', 'Violet']
    
    # 70% Green, 20% Red, 10% Violet වගේ අහඹු තේරීමක්
    # මේ percentages ඔබේ prediction logic එක අනුව වෙනස් කරන්න පුළුවන්
    prediction_color = random.choices(colors, weights=[70, 20, 10], k=1)[0]
    
    # Simple strategy message එකක්
    if prediction_color == 'Green':
        message = "💚 **GREEN** 💚\n\n**Strategy:** Next period Green. Start with small bet."
    elif prediction_color == 'Red':
        message = "❤️ **RED** ❤️\n\n**Strategy:** Next period Red. It's a risk, proceed with caution."
    else: # Violet
        message = "💜 **VIOLET** 💜\n\n**Strategy:** Violet comes less often. Try a combination of Red+Violet or Green+Violet."
    
    return message

# --- Telegram Command Handlers ---

def start(update, context):
    """/start command එකට උත්තර දෙනවා."""
    welcome_message = (
        "👋 **Hello! Welcome to the Wingo Prediction Bot.**\n\n"
        "Remember, all predictions are based on patterns/random logic and are **NOT guaranteed**.\n\n"
        "Use the command below:\n"
        "**/predict** - Get the prediction for the next period."
    )
    update.message.reply_text(welcome_message, parse_mode=telegram.ParseMode.MARKDOWN)

def predict(update, context):
    """/predict command එකට අනාවැකිය දෙනවා."""
    prediction_text = generate_prediction()
    update.message.reply_text(prediction_text, parse_mode=telegram.ParseMode.MARKDOWN)

def main():
    """Bot එක පටන් ගන්නවා."""
    # Updater එක නිර්මාණය කිරීම
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)

    # Dispatcher එක ලබා ගැනීම
    dp = updater.dispatcher

    # Command Handlers එකතු කිරීම
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("predict", predict))

    # Bot එක ක්‍රියාත්මක කිරීම (Polling)
    updater.start_polling()

    # Bot එක නතර කරන තුරු ක්‍රියාත්මක වෙනවා
    updater.idle()

if __name__ == '__main__':
    main()
