import requests
import config
from datetime import datetime
import subprocess
from telegram.ext import *
from config import *
from scrapper import *

PIRATES_CHAT_ID = '-734815817'
KITEBOT_CHAT_ID = '1346459589'


def sample_responses(input_text):
    user_message = str(input_text).lower()

    if user_message in ('hello', 'hi', 'sup', 'hey'):
        return 'Hey, how are you today?'

    if user_message in ('who are you?', 'who are you'):
        return 'I am SkumLeonBot'

    if user_message in ('time', 'time?'):
        now = datetime.now()
        date_time = now.strftime('%d/%m/%y, %H:%M:%S')
        return date_time

    return 'Man you are talking some rubbish'


def get_BCN_wind(update, context):
    wind_dir, wind_kts = scrap_wind_BCN_port()
    message = check_wind_strength_getString(wind_dir, wind_kts)
    telegram_bot.send_msg(message, PIRATES_CHAT_ID)


def handle_message(update, context):
    text = str(update.message.text).lower()
    response = sample_responses(text)
    update.message.reply_text(response)


def send_msg(text, chat_id):
    url_req = 'https://api.telegram.org/bot' + API_KEY + '/sendMessage' + '?chat_id=' + chat_id + '&text=' + text
    results = requests.get(url_req)
    print('Send a message to Telegram')


def launchBot():
    send_msg('******* KiteBot Launched *******', PIRATES_CHAT_ID)

    updater = Updater(API_KEY, use_context=True)

    # Dispatcher
    dp = updater.dispatcher

    # Command Center
    dp.add_handler(CommandHandler('windbcn', get_BCN_wind))

    #dp.add_handler(MessageHandler(Filters.text, handle_message))

    updater.start_polling()
    updater.idle()
    print('Closed Connection to Telegram')
