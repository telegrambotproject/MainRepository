import requests
import pickle
import datetime
import requests
import json
import urllib
import urllib.request as urlrequest
import ssl



now = datetime.datetime.now()


# functions for requests

with open('keys/imdbapi.txt') as f:
    imdb_key = f.read()

with open('keys/apikey.txt') as f:
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


def save_obj(obj, name):  # для базы данных
    with open('obj/' + name + '.pkl', 'wb') as file:
        pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as file:
        return pickle.load(file)


def search_movies(id):  # Не работает, нужно переписать!!!!
    URL = f'https://api.kinohod.ru/api/rest/site/v1/cinemas/{id}/movies'
    PARAMS = {
        'apikey': key,
        'limit': 10,
        'date': now.strftime("%d-%m-%Y")
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    return data


def search_current_movies(movie_number):  # кол-во фильмов
    URL = 'https://api.kinohod.ru/api/rest/site/v1/movies'
    PARAMS = {
        'apikey': key,
        'date': now.strftime("%d-%m-%Y"),
        'limit': movie_number
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    return data


def nearest_cinemas(lat, lon):
    URL = 'https://api.kinohod.ru/api/rest/site/v1/cinemas'
    PARAMS = {
        'apikey': key,
        'latitude': lat,
        'longitude': lon,
        'sort': 'distance'
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    data = sorted(data, key=lambda x: x['distance'])  # Сортировка кинотеатров по растоянию.
    return data


# print(nearest_cinemas(55.730897, 37.629541))

# nearest_cinemas() latitude and longitude from the user
# in the input of the function


def sessions(id, movie_name):
    URL = f'https://api.kinohod.ru/api/rest/site/v1/cinemas/{id}/schedules'
    PARAMS = {
        'apikey': key,
        'date': now.strftime("%d-%m-%Y"),
        'search': movie_name
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    return data


def search_new_by_ganres(ganre):
    URL = 'https://api.kinohod.ru/api/rest/site/v1/movies/recommend'
    PARAMS = {
        'apikey': key
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    for i in range(len(data)):
        for j in range(len(data[i]['genres'])):
            if data[i]['genres'][j]['name'] == ganre:
                print(data[i]['originalTitle'])


# search_new_by_genres('экшен') there are around 30 ganres

def get_id_cinema(cinema_name):
    URL = 'https://api.kinohod.ru/api/rest/site/v1/cinemas'
    PARAMS = {
        'apikey': key
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    for i in range(len(data)):
        if data[i]['shortTitle'] == cinema_name:
            print(data[i]['id'])


# give this function a name of the cinema and it will give you the ID
# Example: get_id('5 Звезд на Новокузнецкой')


def date_conversion(date):  # converting %Y-%m-%d  to %b %d %Y
    date_time_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
    return date_time_obj.strftime('%b %d %Y')


def get_imdb_id(movie_name):  # get imdb id of an upcoming movie
    URL = 'https://api.themoviedb.org/3/search/movie'
    PARAMS = {
        'api_key': imdb_key,
        'query': movie_name
    }
    r = requests.get(url=URL, params=PARAMS)  # Первый реквест, что бы найти фильмы с похожим названием
    data = r.json()
    if r.status_code == 200 and int(data['total_results']) > 0:
        return data
    else:
        print(data)
        return False


def get_future_movies(data):
    film_date = "3000-01-01"
    film_id = "False"
    for m in data['results']:  # Беру ближайший фильм из списка
        if now.strftime("%Y-%m-%d") < m['release_date'] < film_date:
            film_date = m['release_date']
            film_id = m['id']
    if film_id != False:
        URL = 'https://api.themoviedb.org/3/movie/' + str(film_id)
        PARAMS = {
            'api_key': imdb_key,
        }
        r = requests.get(url=URL, params=PARAMS)  # Реквест для нахождения imdb id фильма
        data = r.json()
        film_date = date_conversion(film_date)
        return data.get('imdb_id', [False] * 3)[2], data.get('original_title', False), film_date
    else:
        print(data)
        return False, None, None


def current_movie_list():
    for i in range(1, 2):
        URL = 'https://api.themoviedb.org/3/movie/upcoming'
        PARAMS = {
            'api_key': imdb_key,
            'page': i
        }
        r = requests.get(url=URL, params=PARAMS)  # Первый реквест, что бы найти фильмы с похожим названием
        data = r.json()['results']
        print(data)
        for k in data:
            title = str(k['title'])
            print(f'"{title}","{title}"')


# Поиск мест рядом через google api
# loc = "Широта, Долгота"
# name = "Название места"
def search(loc: str, name, g_key):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {'key': g_key,
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
    from pydub import AudioSegment
    import speech_recognition as sr
    import apiai
    with open('keys/auth.json') as f:  # Ключ для google speech
        credentials = f.read()

    with open('keys/dialogflow.txt') as f:  # Ключ для dialogflow
        dialogflow = f.read()

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
            return text, response
        else:
            return f'I think you said: "{text}", but I did not understand you'
    except sr.UnknownValueError:
        return 'UnknownValueError'
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"


def google_cinema_handler(response):
    response.get('date')


def google_notify_handler():
    pass
