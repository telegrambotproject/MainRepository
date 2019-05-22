import telebot
import requests


def search(query):
    URL = "http://www.omdbapi.com/"
    apikey = "eb2c2cd7"
    PARAMS = {"apikey": apikey,
              "t": query}
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    print(data)
    return data


telebot.apihelper.proxy = {'https': 'https://51.77.210.229:3128'}
bot = telebot.TeleBot('852946157:AAEv1Cg91DaHgGeEgbAKDRvDmm3EGY55nSI')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Ты мне это в глаза скажи, интернет-герой \n'
                                      'Можешь еще фильмец спросить, написав /film')


@bot.message_handler(content_types=['text'])
def start_message(message):
    if message.text == '/film':
        bot.send_message(message.chat.id, "Enter film name")
        bot.register_next_step_handler(message, get_film)


def get_film(message):
    text = message.text
    response = search(text)
    print(text, response)
    bot.send_message(message.chat.id, response['Plot'])
    if response['Poster'] != 'N/A':
        bot.send_photo(message.chat.id, photo=response['Poster'])

# bot.polling()


# STARTING THE IMDB KEYWORDS SEARCH
def key_change(key):
    parts = key.split(' ')
    key = '-'.join(parts).lower()
    return key


def key_search(keys):
    keys_2 = [key_change(k) for k in keys]
    imdb_url = 'https://www.imdb.com/search/keyword'
    params = {"keywords": keys_2}
    r = requests.get(url=imdb_url, params=params)
    return r.text


key_list = ['Hero', 'Violence', 'Tough guy']  # Presumably got it from the text message
print(key_search(key_list))
