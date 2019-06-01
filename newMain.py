import telebot
from urllib.request import urlopen
import functions
import requests



telebot.apihelper.proxy = {'https': 'https://153.92.5.186:8080'}
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
        global list_of_movies
        list_of_movies = functions.search_current_movies()
        markup = telebot.types.ReplyKeyboardMarkup()
        button_1 = telebot.types.KeyboardButton('1')
        button_2 = telebot.types.KeyboardButton('2')
        button_3 = telebot.types.KeyboardButton('3')
        button_4 = telebot.types.KeyboardButton('4')
        button_5 = telebot.types.KeyboardButton('5')
        markup.add(button_1, button_2, button_3, button_4, button_5)
        print(list_of_movies)
        line = ''
        for m in list_of_movies:
            line += f'{m[0]}"{m[1]}", {" ".join(m[2:])}\n'
        bot.send_message(message.chat.id, line)
        bot.send_message(message.chat.id, "Let's get going then! Which of these interest you the most?",
                         reply_markup=markup)
    elif message.text == 'Hell no!':
        markup = telebot.types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, 'I am sorry to hear that',
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Please, choose one of the given two')

@bot.message_handler(content_types=['text'])


bot.polling()
