import telebot
import functions

telebot.apihelper.proxy = {'https': 'https://116.202.43.228:3128'}
bot = telebot.TeleBot('852946157:AAEv1Cg91DaHgGeEgbAKDRvDmm3EGY55nSI')

global d
d = functions.load_obj('data')
print(d)

user_params = {'imdb_id': [], 'favourite_cinema': ''}  # Дефалтный пресет для нового пользователя
remove_markup = telebot.types.ReplyKeyboardRemove()


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in d:  # добавляю нового пользователя в базу данных
        d[message.chat.id] = user_params
        functions.save_obj(d, 'data')  # Сохраняю данные в фаил при помощи pickle
    bot.send_message(message.chat.id, 'List of commands:\n'
                                      '/start - to see all commands\n'
                                      '/movies \n'
                                      '/notify - notify me of upcoming movies\n'
                                      '/my_films - to see or delete your current films\n'
                                      '/forget_me - remove all information about the user', reply_markup=remove_markup)


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
            line += f'"{m["originalTitle"]}", Imdb rating: {m["imdb_rating"]}\n'
        bot.send_message(message.chat.id, line)
        bot.send_message(message.chat.id, "Let's get going then! Which of these interest you the most?",
                         reply_markup=markup)
        bot.register_next_step_handler(message, selected_movie_description)
    elif message.text == 'Hell no!':
        markup = telebot.types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, 'I am sorry to hear that')


def selected_movie_description(message):
    try:
        movie = list_of_movies[int(message.text) - 1]
        print(movie)
        bot.send_message(message.chat.id, movie["annotationFull"])

        markup = telebot.types.ReplyKeyboardMarkup()
        button_1 = telebot.types.KeyboardButton('Yep')
        button_2 = telebot.types.KeyboardButton('Nah')
        markup.add(button_1, button_2)

        bot.send_message(message.chat.id, f'{movie["originalTitle"]}\n\nAre you still interested?',
                         reply_markup=markup)
        bot.register_next_step_handler(message, cinemas_nearby)
    except ValueError:
        bot.send_message(message.chat.id, 'Please, choose one of the given')

# Here we will place a function on location which Kirill is developing!!!
# Next one is supposed to work which users location!


def cinemas_nearby(coordinates):
    functions.nearest_cinemas()


@bot.message_handler(commands=['notify'])  # Функция для напоминания пользователю о выходе новых фильмов
def notify_start(message):
    bot.send_message(message.chat.id, 'Write upcoming movie (movies) you want to be notified about (or multiple ones)\n'
                                      'Ex: Black widow, Spider man')
    bot.register_next_step_handler(message, notify_films)


def notify_films(message):  # Продолжение notify_start()
    global all_film_ids
    all_film_ids = []
    if message.text.lower() == 'cancel':
        bot.send_message(message.chat.id, 'Command canceled', reply_markup=remove_markup)
    else:
        text = ''
        bot.send_chat_action(message.chat.id, 'typing')
        for m in message.text.split(','):
            imdb_id = functions.get_imdb_id(m)  # Запрос стороннему api, для получения imdb id фильма
            if imdb_id[0] != False:
                text += f'"{imdb_id[1]}" will be released in {imdb_id[2]}.\n'
                all_film_ids.append(imdb_id)
        if all_film_ids:
            bot.send_message(message.chat.id, text)

            markup = telebot.types.ReplyKeyboardMarkup()
            button_1 = telebot.types.KeyboardButton('Yes')
            button_2 = telebot.types.KeyboardButton('No')
            button_3 = telebot.types.KeyboardButton('Try another film')
            markup.add(button_1, button_2, button_3)

            bot.send_message(message.chat.id, 'Do you want me to send you notifications?', reply_markup=markup)
            bot.register_next_step_handler(message, add_film_to_user)
        else:
            bot.send_message(message.chat.id, 'I did not understand you. Try another film.\n'
                                              'To exit this command write "cancel"')
            bot.register_next_step_handler(message, notify_films)


def add_film_to_user(message):  # Добавляю фильмы в базу данных пользователя
    if message.text == 'Yes':
        for filmid in all_film_ids:
            if filmid not in d[message.chat.id]['imdb_id']:
                d[message.chat.id]['imdb_id'].append(filmid)
        bot.send_message(message.chat.id, 'Okay, I will notify you when it (they) come out in your cinema \n'
                                          'You can now check all your upcoming films by writing /my_films',
                         reply_markup=remove_markup)
        functions.save_obj(d, 'data')  # Сохраняю данные в фаил при помощи pickle
    elif message.text == 'Try another film':
        bot.send_message(message.chat.id, 'Write upcoming movie (movies) you want to be notified about',
                         reply_markup=remove_markup)
        bot.register_next_step_handler(message, notify_films)
    else:
        bot.send_message(message.chat.id, 'Okay', reply_markup=remove_markup)


@bot.message_handler(commands=['my_films'])  # Команда, которая выдает все отслеживаемые фильмы пользователя.
def user_films(message):
    if d[message.chat.id]['imdb_id']:
        text = ''
        for n, m in enumerate(d[message.chat.id]['imdb_id']):
            text += f'{n + 1}) "{m[1]}" that will be released in {m[2]}.\n'
        bot.send_message(message.chat.id, text)

        markup = telebot.types.ReplyKeyboardMarkup()
        button_1 = telebot.types.KeyboardButton('Yes')
        button_2 = telebot.types.KeyboardButton('No')
        button_3 = telebot.types.KeyboardButton('Clear list')
        markup.add(button_1, button_2, button_3)

        bot.send_message(message.chat.id, 'Do you want to delete any films from this list?', reply_markup=markup)
        bot.register_next_step_handler(message, delete_user_film)
    else:
        bot.send_message(message.chat.id, "You don't have any films in your watch list.\n"
                                          "To add films use /notify command")


def delete_user_film(message):
    if message.text == 'Yes':
        bot.send_message(message.chat.id, 'Write film number (numbers) that you want to delete\n'
                                          'Ex: 2, 4, 5', reply_markup=remove_markup)
        bot.register_next_step_handler(message, delete_user_film2)
    elif message.text == 'Clear list':
        d[message.chat.id]['imdb_id'].clear()
        functions.save_obj(d, 'data')  # Сохраняю данные в фаил при помощи pickle
        bot.send_message(message.chat.id, f'Okay, I cleared everything.', reply_markup=remove_markup)
    elif message.text == 'No':
        bot.send_message(message.chat.id, f'Okay', reply_markup=remove_markup)
    else:
        bot.register_next_step_handler(message, start)


def delete_user_film2(message):  # Продолжение фунуции delete_user_film
    if message.text.lower() == 'cancel':  # Для выхода из цикла, если пользователь продолжает писать неправильный инпут.
        bot.send_message(message.chat.id, 'Operation canceled', reply_markup=remove_markup)
    else:
        try:
            indices = [int(i) - 1 for i in message.text.split(',')]
            for i in sorted(indices, reverse=True):
                del d[message.chat.id]['imdb_id'][i]
            functions.save_obj(d, 'data')  # Сохраняю данные в фаил при помощи pickle
            if d[message.chat.id]['imdb_id']:
                text = ''
                for n, m in enumerate(d[message.chat.id]['imdb_id']):
                    text += f'{n + 1}) "{m[1]}" that will be released in {m[2]}.\n'
                bot.send_message(message.chat.id, 'Films successfully deleted\n'
                                                  f'Here is your new film list:\n{text}', reply_markup=remove_markup)
        except ValueError:
            # Если пользователь ввел что-то кроме цифр
            bot.send_message(message.chat.id, 'I did not understand you\n'
                                              'Write numbers using comma\n'
                                              'Ex: 2, 4, 5\n\n'
                                              'You can also cancel this opreation by typing "cancel"',
                             reply_markup=remove_markup)
            bot.register_next_step_handler(message, delete_user_film2)
        except IndexError:
            # Если к цифре пользователя не назначено никакого фильма
            # (например у пользователя 3 фильма, а он просит удалить 4ый)
            bot.send_message(message.chat.id, 'There is no movie with this number in your movie list\n'
                                              'Write numbers using comma\n'
                                              'Ex: 2, 4, 5\n\n'
                                              'You can also cancel this opreation by typing "cancel"',
                             reply_markup=remove_markup)
            bot.register_next_step_handler(message, delete_user_film2)


@bot.message_handler(commands=['forget_me'])  # Функция для удаления всех данных пользователя
def forget_user(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    button_1 = telebot.types.KeyboardButton('Yes')
    button_2 = telebot.types.KeyboardButton('No')
    markup.add(button_1, button_2)

    bot.send_message(message.chat.id, 'Do really want to delete all information about yourself?\n'
                                      'This process is irreversable.', reply_markup=markup)
    bot.register_next_step_handler(message, delete_user_info)


def delete_user_info(message):
    if message.text == 'Yes':
        d[message.chat.id] = user_params  # Ставлю дефолтные данные на место старых
        functions.save_obj(d, 'data')  # Сохраняю данные в фаил при помощи pickle
        bot.send_message(message.chat.id, 'Your info is deleted.', reply_markup=remove_markup)
    else:
        bot.send_message(message.chat.id, 'Good choice', reply_markup=remove_markup)


bot.polling()
