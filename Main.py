import telebot
import requests
import urllib
import urllib.request as urlrequest
from pydub import AudioSegment
import speech_recognition as sr
import ssl

with open('auth.json') as f:
    credentials = f.read()

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

proxy = {'https': 'https://188.152.158.252:8118'}


proxy_handler = urlrequest.ProxyHandler(proxy)
opener = urlrequest.build_opener(proxy_handler)
urllib.request.install_opener(opener)

telebot.apihelper.proxy = proxy
API_TOKEN = ''
bot = telebot.TeleBot(API_TOKEN)


location = ['']
waypoints = []
waypoint_id = []
key = ""


def search(loc, name, key):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {'key': key,
              'name': name,
              'radius': 1500,
              'location': loc,
              'rankby': 'prominence'}
    r = requests.get(url=url, params=params)
    return r.json()


def route(loc, waypoints, waypoint_id, place_loc):
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


@bot.message_handler(content_types=['location'])
def handle_location(message):
    location[0] = f'{message.location.latitude}, {message.location.longitude}'
    bot.send_message(message.chat.id, "Напиши пару мест через запятую\n Например: Кино, Парк, Ресторан")
    bot.register_next_step_handler(message, get_place)


def get_place(message):
    places = message.text.split(',')
    print(places)
    for p in places:
        response = search(location[0], p, key)
        print(response['results'][0])
        lat = response['results'][0]['geometry']['location']['lat']
        lon = response['results'][0]['geometry']['location']['lng']
        bot.send_message(message.chat.id, response['results'][0]['name'])
        waypoints.append(f'{lat}, {lon}')
        waypoint_id.append(response['results'][0]['place_id'])
    m = route(location[0], waypoints, waypoint_id, location[0])
    print(m)
    bot.send_message(message.chat.id, m)


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    r = sr.Recognizer()
    print(message.voice)
    file_info = bot.get_file(message.voice.file_id)
    file = urllib.request.urlopen(f'https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}')
    with open('audio.ogg', 'wb') as audio:
        audio.write(file.read())
        ogg = AudioSegment.from_ogg("audio.ogg")
        ogg.export("audio.wav", format="wav")
    with sr.AudioFile('audio.wav') as source:
        audio = r.record(source)
        try:
            text = r.recognize_google_cloud(audio, credentials_json=credentials)
            bot.send_message(message.chat.id, text)
        except sr.UnknownValueError:
            bot.send_message(message.chat.id, 'Не понял')
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")


bot.polling()
