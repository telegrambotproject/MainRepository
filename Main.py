import telebot
import requests


telebot.apihelper.proxy = {'https': 'https://217.23.6.40:3128'}
bot = telebot.TeleBot('852946157:AAEv1Cg91DaHgGeEgbAKDRvDmm3EGY55nSI')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Ты мне это в глаза скажи, интернет-герой \n'
                                      'Можешь еще фильмец спросить, написав /film')


@bot.message_handler(content_types=['location'])
def handle_location(message):
    print("{0}, {1}".format(message.location.latitude, message.location.longitude))



bot.polling()
