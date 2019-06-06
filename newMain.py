import telebot
import functions

telebot.apihelper.proxy = {'https': 'https://116.202.43.228:3128'}
bot = telebot.TeleBot('852946157:AAEv1Cg91DaHgGeEgbAKDRvDmm3EGY55nSI')

global d
d = functions.load_obj('data')


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in d:  # добавляю нового пользователя в базу данных
        d[message.chat.id] = {}
        functions.save_obj(d, 'data')
    bot.send_message(message.chat.id, 'List of commands:\n /start - to see all commands\n '
                                      '/movies \n'
                                      '/notify - notify me of upcoming movies')


@bot.message_handler(commands=['movies'])
def movies(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    button_1 = telebot.types.KeyboardButton('Yes, please!')
    button_2 = telebot.types.KeyboardButton('Hell no!')
    markup.add(button_1, button_2)
    bot.send_message(message.chat.id, 'Hello there! Wanna see some movies?',
                     reply_markup=markup)
    bot.register_next_step_handler(message, first_chose)

def first_chose(message):
    if message.text == 'Yes, please!':
        global list_of_movies
        list_of_movies = functions.search_current_movies(5)
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=3)
        button_1 = telebot.types.KeyboardButton('1')
        button_2 = telebot.types.KeyboardButton('2')
        button_3 = telebot.types.KeyboardButton('3')
        button_4 = telebot.types.KeyboardButton('4')
        button_5 = telebot.types.KeyboardButton('5')
        markup.add(button_1, button_2, button_3, button_4, button_5)
        line = ''
        for m in list_of_movies:
            line += f'{m[1]}"{m[2]}", {" ".join(m[3:])}\n'
        bot.send_message(message.chat.id, line)
        bot.send_message(message.chat.id, "Let's get going then! Which of these interest you the most?",
                         reply_markup=markup)
        bot.register_next_step_handler(message, selected_movie_description)
    elif message.text == 'Hell no!':
        markup = telebot.types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, 'I am sorry to hear that')

def selected_movie_description(message):
    try:
        movie = functions.search_movies(list_of_movies[int(message.text) - 1][0])
        print(movie)
        markup = telebot.types.ReplyKeyboardMarkup()
        button_1 = telebot.types.KeyboardButton('Yep')
        button_2 = telebot.types.KeyboardButton('Nah')
        markup.add(button_1, button_2)
        bot.send_message(message.chat.id, f'{movie[0]["annotationFull"]}\n\nAre you still interested?',
                         reply_markup=markup)
        bot.register_next_step_handler(message, cinemas_nearby)
    except ValueError:
        bot.send_message(message.chat.id, 'Please, choose one of the given')

# Here we will place a function on location which Kirill is developing!!!
# Next one is supposed to work which users location!

def cinemas_nearby(coordinates):
    functions.nearest_cinemas()



@bot.message_handler(commands=['notify'])
def notify(message):
    bot.send_message(message.chat.id, 'Write upcoming movie/movies you want to be notified about (or multiple ones)\n'
                                      'Ex: Black widow, Spider man')
    bot.register_next_step_handler(message, notify_films)

def notify_films(message):
    #imdb_id = functions.get_imdb_id(message.text)
    imdb_id = '6320628'
    #d.setdefault(message.chat.id, message.chat.id).get()


bot.polling()
