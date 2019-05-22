import telebot
import requests



def search(loc, name):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    key = ""
    params = {'key': key,
              'name': name,
              'radius': 1500,
              'location': loc}
    r = requests.get(url=url, params=params)
    print(r.json())
    return r.json()


telebot.apihelper.proxy = {'https': 'https://188.152.158.252:8118'}
bot = telebot.TeleBot('852946157:AAEv1Cg91DaHgGeEgbAKDRvDmm3EGY55nSI')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Ты где НАХОДИШЬСЯ? Ара, я найду тебя! Метку поставь!')


@bot.message_handler(content_types=['location'])
def handle_location(message):
    global location
    location = f'{message.location.latitude}, {message.location.longitude}'
    bot.send_message(message.chat.id, "Что ты хочешь найти?")
    bot.register_next_step_handler(message, get_place)


def get_place(message):
    place = message.text
    response = search(location, place)
    print(place, response['results'][0])
    lat = response['results'][0]['geometry']['location']['lat']
    lon = response['results'][0]['geometry']['location']['lng']
    bot.send_location(message.chat.id, lat, lon)


bot.polling()
