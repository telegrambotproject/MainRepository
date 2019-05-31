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

#functions for requests

with open('apikey.txt') as f:
    key = f.read()

def search_movies(id):
    URL = 'https://api.kinohod.ru/api/rest/site/v1/movies'
    PARAMS = {
        'apikey':key,
        'id':id
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    return data

#Example: id = 23211
#print(search_movies(23211))

def search_current_movies():
    URL = 'https://api.kinohod.ru/api/rest/site/v1/movies/recommend'
    PARAMS = {
        'apikey':key
    }
    r = requests.get(url=URL,params=PARAMS)
    data = r.json()
    for i in range(5):
        print(f'{data[i]["originalTitle"]},  IMDB rating: {data[i]["imdb_rating"]}')


def nearest_cinemas():
    URL = 'https://api.kinohod.ru/api/rest/site/v1/cinemas'
    PARAMS = {
        'apikey':key,
        'sort':5000,
        'city':1,
        'title':"Кинотеатр «5 Звезд на Павелецкой»",
        'timeBeforeSeance':60,
        'latitude':55.921336,
        'longitude':37.991876
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    for i in range(5):
        print(data[i]['shortTitle'], data[i]['mall'], data[i]['phones'][0]['number'])

#nearest_cinemas() latitude and longitude from the user
#in the input of the function

def movies_in_cinema(id):
    URL = f'https://api.kinohod.ru/api/rest/site/v1/cinemas/{id}/movies'
    URLname = f'https://api.kinohod.ru/api/rest/site/v1/cinemas/{id}'
    PARAMSname = {
        'apikey':key
    }
    PARAMS = {
        'apikey':key
    }
    rname = requests.get(url=URLname, params=PARAMSname)
    dataname = rname.json()
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    cinemaname = dataname['shortTitle']
    print(f'Movies in {cinemaname} are:')
    for i in range(5):
        print(data[i]["originalTitle"])

#movies_in_cinema(227)
#227 = id of the particular cinema

def search_new_by_ganres(ganre):
    URL = 'https://api.kinohod.ru/api/rest/site/v1/movies/recommend'
    PARAMS = {
        'apikey':key
    }
    r = requests.get(url=URL,params=PARAMS)
    data = r.json()
    for i in range((len(data)) - 1):
        for j in range((len(data[i]['genres']) - 1)):
            if data[i]['genres'][j]['name'] == ganre:
                print(data[i]['originalTitle'])

#search_new_by_ganres('экшен') there are around 30 ganres