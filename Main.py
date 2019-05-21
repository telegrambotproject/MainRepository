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

bot.polling()

#### STARTING THE IMDB KEYWORDS SEARCH
lists_of_keywords = ['Action Hero', 'Tough Guy', 'Violence'] # Presumably got it from the text message

IMDB_URL = 'https://www.imdb.com/search/keyword?keywords='
additional_query = '&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=7846868c-8414-4178-8f43-9ad6b2ef0baf&pf_rd_r=Y51P6Q4PPA4PTDTZG5AP&pf_rd_s=center-1&pf_rd_t=15051&pf_rd_i=moka&ref_=kw_ref_key&sort=moviemeter,asc&mode=detail&page=1'


def keywords_reformation(keyword):
    parts = keyword.split(' ')
    the_keyword = '-'.join(parts)
    the_keyword = the_keyword.lower()
    return the_keyword


def search_by_keyword(keywords):
    query = ''
    the_keyword = ''
    query = str(keywords_reformation(keywords[0]))
    for i in range(1, len(keywords)):
        the_keyword = keywords_reformation(keywords[i])
        query = str(query + '%2C' + the_keyword)
    return query


Final_URL = str(IMDB_URL + search_by_keyword(lists_of_keywords) + additional_query)
print(Final_URL)
