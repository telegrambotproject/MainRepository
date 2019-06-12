import telebot
import functions
import urllib
from datetime import datetime
import threading

proxy = {'https': 'https://95.216.119.75:3128'}
telebot.apihelper.proxy = proxy
API_TOKEN = '852946157:AAEv1Cg91DaHgGeEgbAKDRvDmm3EGY55nSI'
bot = telebot.TeleBot(API_TOKEN)


def_params = {'location': '',
              'waypoints': [],
              'waypoint_id': [],
              'info_cinema': [],
              'list_of_movies': []
              }

temp_info = {}


global d
d = functions.load_obj('data')
print(d)

user_params = {'imdb_id': [], 'favourite_cinema': ''}  # Дефалтный пресет для нового пользователя
remove_markup = telebot.types.ReplyKeyboardRemove()

functions.request_proxy(proxy)
functions.fake_ssl()


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
                                      '/favourite_cinema - set your favourite cinema \n'
                                      '/route - make a route\n'
                                      '/forget_me - remove all information about the user', reply_markup=remove_markup)


@bot.message_handler(commands=['movies'])
def movies(message):
    bot.send_chat_action(message.chat.id, 'typing')
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    button_1 = telebot.types.KeyboardButton('Yes')
    button_2 = telebot.types.KeyboardButton('No')
    markup.add(button_1, button_2)
    bot.send_message(message.chat.id, 'Hello there! Wanna see some movies?',
                     reply_markup=markup)
    bot.register_next_step_handler(message, location)


def location(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        if message.text == 'Yes':
            bot.send_message(message.chat.id, 'Okay! Then please send me your location!')
            bot.register_next_step_handler(message, cinemas_nearby)
        elif message.text == 'No':
            bot.send_message(message.chat.id, 'Alright, then please, choose something else!')
            bot.register_next_step_handler(message, start)
    except ValueError:
        bot.send_message(message.chat.id, 'Please, choose one of the given')


def cinemas_nearby(coordinates):
    try:
        latitude = coordinates.location.latitude
        longitude = coordinates.location.longitude
        temp_info.setdefault(coordinates.chat.id, def_params)
        temp_info[coordinates.chat.id]['info_cinema'] = functions.nearest_cinemas(latitude, longitude)
        info_cinema = temp_info[coordinates.chat.id]['info_cinema']
        bot.send_chat_action(coordinates.chat.id, 'typing')
        bot.send_message(coordinates.chat.id, f'Here you go! The closest cinema is called "{info_cinema[0]["shortTitle"]}"')
        bot.send_location(coordinates.chat.id, info_cinema[0]['location']['latitude'],
                          info_cinema[0]['location']['longitude'])
        temp_info[coordinates.chat.id]['list_of_movies'] = functions.search_movies(info_cinema[0]['id'])
        list_of_movies = temp_info[coordinates.chat.id]['list_of_movies']
        print(list_of_movies)
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        for i, j in enumerate(list_of_movies):
            markup.add(f'{i + 1}. {j["originalTitle"]},'
                       f' {j["imdb_rating"]}')
        bot.send_message(coordinates.chat.id,
                         "Let's get going then! Here are top 5 movies which are now ongoing and their IMDB rating!"
                         " Which of these interest you the most?", reply_markup=markup)
        bot.register_next_step_handler(coordinates, selected_movie_description)
    except AttributeError:
        bot.send_message(coordinates.chat.id, 'Please, choose one of the given')


def selected_movie_description(message):
    bot.send_chat_action(message.chat.id, 'typing')
    a, b = message.text.split(', ')
    a = a[2:]
    global chosen_movie
    chosen_movie = a
    try:
        list_of_movies = temp_info[message.chat.id]['list_of_movies']
        movie = list_of_movies[int(message.text[0]) - 1]
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        button_1 = telebot.types.KeyboardButton('Yes')
        button_2 = telebot.types.KeyboardButton('No')
        markup.add(button_1, button_2)
        bot.send_message(message.chat.id, f'{movie["annotationFull"]}\n\nAre you still interested?',
                         reply_markup=markup)
        bot.register_next_step_handler(message, movie_sessions)
    except ValueError:
        bot.send_message(message.chat.id, 'Please, choose one of the given')


def movie_sessions(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        schedule = ''
        if message.text == 'Yes':
            info_cinema = temp_info[message.chat.id]['info_cinema']
            info_movies = functions.sessions(info_cinema[0]['id'], chosen_movie)
            for m in info_movies[0]["schedules"]:
                schedule += f'{m["time"]}\n'
            bot.send_message(message.chat.id, f'And these are the closest sessions:\n{schedule}')
    except ValueError:
        bot.send_message(message.chat.id, 'Please, choose one of the given')

    # Название кинотеатра


# Расписание
# Любимые кинотеатры
# -------------------------------------- This line divides the functionality of a bot: current movies and future movies

@bot.message_handler(commands=['favourite_cinema'])
def favourite_cinema(message):
    bot.send_message(message.chat.id, "Send your favourite cinema location")
    bot.register_next_step_handler(message, favourite_cinema2)


def favourite_cinema2(message):
    try:
        if message.content_type == "location":
            latitude = message.location.latitude
            longitude = message.location.longitude
            temp_info[message.chat.id]['info_cinema'] = functions.nearest_cinemas(latitude, longitude)
            info_cinema = temp_info[message.chat.id]['info_cinema']
            bot.send_chat_action(message.chat.id, 'typing')
            bot.send_message(message.chat.id,
                             f'I have set your favourite cinema to "{info_cinema[0]["shortTitle"]}"')
            d[message.chat.id]["favourite_cinema"] = str(info_cinema[0]['id'])
            functions.save_obj(d, 'data')
        else:
            bot.send_message(message.chat.id,
                             f'You did not send the location')
    except:
        pass



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
            imdb_ids = functions.get_imdb_id(m)  # Запрос стороннему api, для получения imdb id фильма
            if imdb_ids != False:
                upcoming_f = functions.get_future_movies(imdb_ids)
                if upcoming_f[0] != False:
                    text += f'"{upcoming_f[1]}" will be released in {upcoming_f[2]}.\n'
                    all_film_ids.append(upcoming_f)
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


@bot.message_handler(commands=['route'])  # Беру локацию от пользователя
def get_user_location(message):
    bot.send_message(message.chat.id, "Send your location.")
    bot.register_next_step_handler(message, handle_location)


def handle_location(message):
    if message.content_type == "location":
        temp_info.setdefault(message.chat.id, def_params)
        temp_info[message.chat.id]['location'] = f'{message.location.latitude}, {message.location.longitude}'  # задаю глобальный параметр location.
        bot.send_message(message.chat.id, "Напиши пару мест через запятую\n Например: Кино, Парк, Ресторан")
        bot.register_next_step_handler(message, get_places)


def get_places(message):  # Поиск множества мест
    with open('keys/g_key.txt') as f:  # Ключ для google api
        global g_key
        g_key = f.read()
    places = message.text.split(',')
    print(places)
    for p in places:
        response = functions.search(temp_info[message.chat.id]['location'], p, g_key)
        print(response['results'][0])
        lat = response['results'][0]['geometry']['location']['lat']
        lon = response['results'][0]['geometry']['location']['lng']
        bot.send_message(message.chat.id, response['results'][0]['name'])
        temp_info[message.chat.id]['waypoints'].append(f'{lat}, {lon}')
        temp_info[message.chat.id]['waypoint_id'].append(response['results'][0]['place_id'])
    m = functions.route(temp_info[message.chat.id]['location'],
                        temp_info[message.chat.id]['waypoints'],
                        temp_info[message.chat.id]['waypoint_id'])
    temp_info[message.chat.id] = def_params
    print(m)
    bot.send_message(message.chat.id, m)


@bot.message_handler(commands=['voice'])
def voice(message):
    if d[message.chat.id]["favourite_cinema"]:
        bot.send_message(message.chat.id, "Please set up your favourite cinema by typing /favourite_cinema "
                                          "to use voice commans\n"
                                          "You can change it at any time")
    else:
        bot.send_message(message.chat.id, "Now say your command to bot")
        bot.register_next_step_handler(message, handle_voice)


def handle_voice(message):  # голосовые команды
    if message.content_type == 'voice':
        print(message.voice)
        file_info = bot.get_file(message.voice.file_id)
        # рекветс через проксти, тк телеграм заблочен.
        file = urllib.request.urlopen(f'https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}')
        response = functions.google_speech_request(file)
        try:
            if not response['movie-notify']:
                functions.google_cinema_handler()
        except IndexError:
            bot.send_message(message.chat.id, response)
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "You did not use voice message. Try again by typing /voice")

#notification delivery
def notify(d):
    for id, info in d.items():
        for i in info['imdb_id']:
            date_time_obj = datetime.strptime(i[2], '%b %d %Y')
            if datetime.now() >= date_time_obj:
                bot.send_message(id, f'Your favourite movie {i[1]} is coming out tomorrow!')
                index = info['imdb_id'].index(i)
                info['imdb_id'].pop(index)
                functions.save_obj(d, 'data')

threading.Timer(21600.0, notify(d)).start()

bot.polling()
