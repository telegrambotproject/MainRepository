import telebot
import requests
import urllib
import urllib.request as urlrequest
from pydub import AudioSegment
import speech_recognition as sr
import apiai, json
import ssl

with open('info/auth.json') as f:
    credentials = f.read()
with open('info/dialogflow.txt') as f:
    dialogflow = f.read()
with open('info/key.txt') as f:
    key = f.read()

try:  # Создаю поддельный SSL сертификат
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


proxy = {'https': 'https://188.152.158.252:8118'}


proxy_handler = urlrequest.ProxyHandler(proxy)
opener = urlrequest.build_opener(proxy_handler)
urllib.request.install_opener(opener)  # Установка прокси для запроса фаилов в телеграме.


telebot.apihelper.proxy = proxy  # Прокси для телеграм бота бота
API_TOKEN = '852946157:AAEv1Cg91DaHgGeEgbAKDRvDmm3EGY55nSI'
bot = telebot.TeleBot(API_TOKEN)


location = ['']
waypoints = []
waypoint_id = []


# Поиск мест рядом через google api
# loc = "Широта, Долгота"
# name = "Название места"
def search(loc: str, name, key):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {'key': key,
              'name': name,
              'radius': 1500,
              'location': loc,
              'rankby': 'prominence'}
    r = requests.get(url=url, params=params)
    return r.json()


# loc = "Широта, Долгота" (место начала)
# waypoints = ["Широта, Долгота", ...] (указывать все места по порядку)
# waypoint_id = [id места, ...] (Опционально, но нельзя указывать отдельно от параметра waypoints.)
def route(loc, waypoints, waypoint_id):
    url = 'https://www.google.com/maps/dir/'
    params = {'api': '1',
              'origin': loc,
              'waypoints': '|'.join(waypoints[:-1]),
              'waypoint_place_ids': '|'.join(waypoint_id[:-1]),
              'destination': waypoints[-1],
              'destination_place_id': waypoint_id[-1],
              'travelmode': 'walking'}
    p = requests.Request('GET', url=url, params=params).prepare()
    print(p.url)
    waypoints.clear()
    waypoint_id.clear()
    return p.url


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Пришли геолокацию.')


@bot.message_handler(content_types=['location'])  # Беру локацию от пользователя
def handle_location(message):
    location[0] = f'{message.location.latitude}, {message.location.longitude}'  # задаю глобальный параметр location.
    bot.send_message(message.chat.id, "Напиши пару мест через запятую\n Например: Кино, Парк, Ресторан")
    bot.register_next_step_handler(message, get_places)


def get_places(message):  # Поиск множества мест
    places = message.text.split(',')
    print(places)
    for p in places:
        response = search(location[0], p, key)  # параметр location - глобальный.
        print(response['results'][0])
        lat = response['results'][0]['geometry']['location']['lat']
        lon = response['results'][0]['geometry']['location']['lng']
        bot.send_message(message.chat.id, response['results'][0]['name'])
        waypoints.append(f'{lat}, {lon}')
        waypoint_id.append(response['results'][0]['place_id'])
    m = route(location[0], waypoints, waypoint_id)
    print(m)
    bot.send_message(message.chat.id, m)


@bot.message_handler(content_types=['voice'])  # Функция ловит все голосовые сообщения
def handle_voice(message):
    r = sr.Recognizer()  # нужно для библиотеки "speech_recognition"
    print(message.voice)
    file_info = bot.get_file(message.voice.file_id)
    # рекветс через проксти, тк телеграм заблочен.
    file = urllib.request.urlopen(f'https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}')
    with open('audio.ogg', 'wb') as audio:  # сохраняю аудио на компьютер.
        audio.write(file.read())
        ogg = AudioSegment.from_ogg("audio.ogg")  # Переконвертация в формат wav
        ogg.export("audio.wav", format="wav")
    with sr.AudioFile('audio.wav') as source:
        audio = r.record(source)
        try:
            text = r.recognize_google_cloud(audio, credentials_json=credentials)  # запрос google speech
            request = apiai.ApiAI(dialogflow).text_request()
            request.lang = 'en'
            request.query = text
            bot.send_message(message.chat.id, text)
            responseJson = json.loads(request.getresponse().read().decode('utf-8'))
            print(responseJson)
            response = responseJson['result']['fulfillment']['speech']  # Разбираем JSON и вытаскиваем ответ
            # Если есть ответ от бота - присылаем юзеру, если нет, то гугл не разобрал аудио.
            if response:
                bot.send_message(message.chat.id, text=response)
            else:
                bot.send_message(message.chat.id, text='I did not understand you')
        except sr.UnknownValueError:
            bot.send_message(message.chat.id, 'UnknownValueError')
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")


bot.polling()
