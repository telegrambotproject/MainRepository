import telebot
from urllib.request import urlopen
import requests


telebot.apihelper.proxy = {'https': 'https://54.39.24.33:3128'}
bot = telebot.TeleBot('852946157:AAEv1Cg91DaHgGeEgbAKDRvDmm3EGY55nSI')


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    button_1 = telebot.types.KeyboardButton('Yes, please!')
    button_2 = telebot.types.KeyboardButton('Hell no!')
    markup.add(button_1, button_2)
    bot.send_message(message.chat.id, 'Hello there! Wanna see some movies?',
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def first_chose(message):
    if message.text == 'Yes, please!':
        markup = telebot.types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "Let's get going then",
                         reply_markup=markup)
        request = 'http://api.kinopoisk.cf/getTodayFilms'
        response_body = urlopen(request).read()
        bot.send_message(message.chat.id, response_body)
    elif message.text == 'Hell no!':
        markup = telebot.types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, 'I am sorry to hear that',
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Please, choose one of the given two')


bot.polling()
