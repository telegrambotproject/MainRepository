import telebot
import functions

telebot.apihelper.proxy = {'https': 'https://95.216.119.75:3128'}
bot = telebot.TeleBot('852946157:AAEv1Cg91DaHgGeEgbAKDRvDmm3EGY55nSI')

count = 0

global d
d = functions.load_obj('data')
print(d)

user_params = {'imdb_id': [], 'favourite_cinema': ''}  # Дефалтный пресет для нового пользователя
remove_markup = telebot.types.ReplyKeyboardRemove()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_chat_action(message.chat.id, 'typing')
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
    button_1 = telebot.types.KeyboardButton('Yes')
    button_2 = telebot.types.KeyboardButton('No!')
    markup.add(button_1, button_2)
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Hello there! Wanna see some movies?',
                     reply_markup=markup)
    bot.register_next_step_handler(message, first_choice)


def first_choice(message):
    global count
    bot.send_chat_action(message.chat.id, 'typing')
    if (message.text == 'No' and count >= 1) or message.text == 'Yes':
        global list_of_movies
        list_of_movies = functions.search_current_movies(5)
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        for _ in range(5):
            markup.add(f'{_ + 1}. {list_of_movies[_]["originalTitle"]},'
                       f' {list_of_movies[_]["imdb_rating"]}')
        bot.send_message(message.chat.id, "Let's get going then! Here are top 5 movies which are now ongoing!"
                                          "Which of these interest you the most?", reply_markup=markup)
        bot.register_next_step_handler(message, selected_movie_description)
        count += 1
    elif message.text == 'No':
        bot.send_message(message.chat.id, 'I am sorry to hear that!'
                                          ' You can go mack to the movie menu by typing "/movie".'
                                          'Or you may type "/start" to start all over again.')
    else:
        bot.send_message(message.chat.id, 'Please, choose one of the given two!')
        movies(message)


@bot.message_handler(commands=['discription'])
def selected_movie_description(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        movie = list_of_movies[int(message.text[0]) - 1]
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        button_1 = telebot.types.KeyboardButton('Yes')
        button_2 = telebot.types.KeyboardButton('No')
        markup.add(button_1, button_2)
        bot.send_message(message.chat.id, f'{ movie["annotationFull"]}\n\nAre you still interested?',
                         reply_markup=markup)
        bot.register_next_step_handler(message, selected_movie_description_2)
    except ValueError:
        bot.send_message(message.chat.id, 'Please, choose one of the given')


def selected_movie_description_2(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        if message.text == 'Yes':
            bot.send_message(message.chat.id, 'Okay! Then please send me your location!')
            bot.register_next_step_handler(message, cinemas_nearby)
        elif message.text == 'No':
            bot.send_message(message.chat.id, 'Alright, then please, choose something else!')
            first_choice(message)
    except ValueError:
        bot.send_message(message.chat.id, 'Please, choose one of the given')


def cinemas_nearby(coordinates):
    latitude = coordinates.location.latitude
    longitude = coordinates.location.longitude
    info_cinema = functions.nearest_cinemas(latitude, longitude)
    bot.send_chat_action(coordinates.chat.id, 'typing')
    bot.send_message(coordinates.chat.id, f'Here you go! The closest cinema is called "{info_cinema[0]["shortTitle"]}"')
    bot.send_location(coordinates.chat.id, info_cinema[0]['location']['latitude'],
                      info_cinema[0]['location']['longitude'])
    functions.movies_in_cinema(info_cinema[0]['id'])

# Название кинотеатра
# Расписание
# Любимые кинотеатры
# -------------------------------------- This line divides the functionality of a bot: current movies and future movies


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
