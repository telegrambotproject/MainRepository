import telebot
import urllib
import functions


with open('info/key.txt') as f:  # Ключ для google api
    key = f.read()


proxy = {'https': 'https://188.152.158.252:8118'}

functions.request_proxy(proxy)
functions.fake_ssl()

telebot.apihelper.proxy = proxy  # Прокси для телеграм бота бота
API_TOKEN = ''
bot = telebot.TeleBot(API_TOKEN)


location = ['']
waypoints = []
waypoint_id = []


@bot.message_handler(content_types=['location'])  # Беру локацию от пользователя
def handle_location(message):
    location[0] = f'{message.location.latitude}, {message.location.longitude}'  # задаю глобальный параметр location.
    bot.send_message(message.chat.id, "Напиши пару мест через запятую\n Например: Кино, Парк, Ресторан")
    bot.register_next_step_handler(message, get_places)


def get_places(message):  # Поиск множества мест
    places = message.text.split(',')
    print(places)
    for p in places:
        response = functions.search(location[0], p, key)  # параметр location - глобальный.
        print(response['results'][0])
        lat = response['results'][0]['geometry']['location']['lat']
        lon = response['results'][0]['geometry']['location']['lng']
        bot.send_message(message.chat.id, response['results'][0]['name'])
        waypoints.append(f'{lat}, {lon}')
        waypoint_id.append(response['results'][0]['place_id'])
    m = functions.route(location[0], waypoints, waypoint_id)
    print(m)
    bot.send_message(message.chat.id, m)


@bot.message_handler(content_types=['voice'])  # Функция ловит все голосовые сообщения
def handle_voice(message):
    print(message.voice)
    file_info = bot.get_file(message.voice.file_id)
    # рекветс через проксти, тк телеграм заблочен.
    file = urllib.request.urlopen(f'https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}')
    response = functions.google_speech_request(file)
    bot.send_message(message.chat.id, response)




bot.polling()
