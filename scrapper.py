import telegram_bot
from telegram_bot import *
from lxml import html
from bs4 import BeautifulSoup
import requests
import re
import time
import string
import threading

PIRATES_CHAT_ID = '-734815817'
KITEBOT_CHAT_ID = '1346459589'
CONVERSION_CONSTANT = 1.852
TWINTIP_KTS_THRESHOLD = 13.9


def scrap_wind_strength(wind_and_dir_str):

    string_script_wind_slice = wind_and_dir_str[115:140]
    wind_digits_string = re.sub('\D', '', string_script_wind_slice)

    speed_digits = wind_digits_string.replace('1852', '')
    knots = str
    if len(speed_digits) == 2:
        digit1 = speed_digits[0]
        digit2 = speed_digits[1]
        knots = digit1 + '.' + digit2
    elif len(speed_digits) == 3:
        digit1 = speed_digits[0]
        digit2 = speed_digits[1]
        digit3 = speed_digits[2]
        knots = digit1 + digit2 + '.' + digit3
    else:
        print('Unexpected digit length')
    knots = float(knots) / CONVERSION_CONSTANT
    knots = round(knots, 2)

    return knots


def scrap_wind_dir(wind_and_dir_str):

    whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    string_script_dir_slice = wind_and_dir_str[63:71]
    direction = ''.join(filter(whitelist.__contains__, string_script_dir_slice))

    return direction


def scrap_wind_BCN_port():

    html_text = requests.get('https://www.velabarcelona.com/').text
    soup = BeautifulSoup(html_text, "lxml")
    jobs = soup.find_all('script')
    script_wind_and_dir = jobs[17]
    string_script_wind_and_dir = str(script_wind_and_dir)

    # scrap knots
    wind_knots = scrap_wind_strength(string_script_wind_and_dir)
    # print(wind_knots)

    # scrap direction
    dir = scrap_wind_dir(string_script_wind_and_dir)

    # print(wind_dir)

    return dir, wind_knots


def check_wind_strength_getString(direction, knots):
    msg_string = str
    if knots < 8:
        msg_string = 'BCN: ' + direction + ' ' + str(knots) + ' kts' + ' - Poco viento. Ponte a beber una birra y navega mas tarde!'
    elif 8 <= knots < 13.9:
        msg_string = 'BCN: ' + direction + ' ' + str(knots) + ' kts' + ' - ¡Ya está pa foil!'
    elif 13.9 <= knots < 15:
        msg_string = 'BCN: ' + direction + ' ' + str(knots) + ' kts' + ' - ¡Un mal día navegando es mejor que un buen día trabajando!!'
    elif 15 <= knots < 25:
        msg_string = 'BCN: ' + direction + ' ' + str(knots) + ' kts' + ' - ¡Sin viento, sin gloria! VAMOS PIRATES!'
    elif 25 <= knots < 30:
        msg_string = 'BCN: ' + direction + ' ' + str(knots) + ' kts' + ' - ¡La imaginación es la cometa más alta que se puede volar! VAMOS PIRATES!!'
    elif 30 <= knots:
        msg_string = 'BCN: ' + direction + ' ' + str(knots) + ' kts' + ' - Luna! Luna! Luna! Luna!'
    return msg_string


def listAverage(lst):
    return sum(lst) / len(lst)


if __name__ == "__main__":
    try:

        telegram_bot_thread = threading.Thread(target=telegram_bot.launchBot)
        telegram_bot_thread.start()

        while True:
            wind_kts = 0
            wind_dir = str
            wind_knots_list = []
            for i in range(3):
                wind_dir, wind_kts = scrap_wind_BCN_port()
                wind_knots_list.append(wind_kts)
                time.sleep(60 * 10)
                print(wind_knots_list)

            wind_kts = listAverage(wind_knots_list)
            message = check_wind_strength_getString(wind_dir, wind_kts)

            if wind_kts > TWINTIP_KTS_THRESHOLD:
                telegram_bot.send_msg(message, PIRATES_CHAT_ID)

            # and \
            #         (wind_dir != 'N') and \
            #         wind_dir != 'NW' and \
            #         wind_dir != 'W':

    except Exception as e:
        print(str(e))
        print('TelegramBot Crashed, re-running it')
