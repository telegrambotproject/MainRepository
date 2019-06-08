import requests
from pydub import AudioSegment
import speech_recognition as sr
import apiai, json
import urllib
import urllib.request as urlrequest
import ssl


with open('info/auth.json') as f:  # Ключ для google speech
    credentials = f.read()
with open('info/dialogflow.txt') as f:  # Ключ для dialogflow
    dialogflow = f.read()
with open('info/key.txt') as f:  # Ключ для google api
    key = f.read()


def request_proxy(proxy):
    proxy_handler = urlrequest.ProxyHandler(proxy)
    opener = urlrequest.build_opener(proxy_handler)
    urllib.request.install_opener(opener)  # Установка прокси для запроса фаилов в телеграме.


def fake_ssl():
    try:  # Создаю поддельный SSL сертификат
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context


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


def google_speech_request(file):
    r = sr.Recognizer()  # нужно для библиотеки "speech_recognition"
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
        print(text)
        responseJson = json.loads(request.getresponse().read().decode('utf-8'))
        print(responseJson)
        response = responseJson['result']['contexts'][0]['parameters']  # Разбираем JSON и вытаскиваем ответ
        # Если есть ответ от бота - присылаем юзеру, если нет, то гугл не разобрал аудио.
        if response:
            return f'You said: "{text}"\nBot responded: "{response}"'
        else:
            return f'I think you said: "{text}", but I did not understand you'
    except sr.UnknownValueError:
        return 'Error: UnknownValueError'
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"
