import requests
import pickle
import datetime
now = datetime.datetime.now()


# functions for requests

with open('keys/imdbapi.txt') as f:
    imdb_key = f.read()

with open('keys/apikey.txt') as f:
    key = f.read()


def save_obj(obj, name):  # для базы данных
    with open('obj/' + name + '.pkl', 'wb') as file:
        pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as file:
        return pickle.load(file)

    
def search_movies(movie_id):  # Не работает, нужно переписать!!!!
    URL = 'https://api.kinohod.ru/api/rest/site/v1/movies/' + str(movie_id)
    print(URL)
    PARAMS = {
        'apikey': key
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    print(data)
    return data[0]['originalTitle'], data[0]['annotationFull'], data[0]['genres'][0]['name']

# Example: id = 23211
# print(search_movies(23211))

# Vova: I changed the return of def below so that it fits the bot messages


def search_current_movies(movie_number):  # кол-во фильмов
    URL = 'https://api.kinohod.ru/api/rest/site/v1/movies/recommend'
    PARAMS = {
        'apikey': key,
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


def movies_in_cinema(id, movie_name):
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
        'apikey':key
    }
    r = requests.get(url=URL,params=PARAMS)
    data = r.json()
    for i in range(len(data)):
        for j in range(len(data[i]['genres'])):
            if data[i]['genres'][j]['name'] == ganre:
                print(data[i]['originalTitle'])

# search_new_by_genres('экшен') there are around 30 ganres

def get_id_cinema(cinema_name):
    URL = 'https://api.kinohod.ru/api/rest/site/v1/cinemas'
    PARAMS = {
        'apikey':key
    }
    r = requests.get(url=URL,params=PARAMS)
    data = r.json()
    for i in range(len(data)):
        if data[i]['shortTitle'] == cinema_name:
            print(data[i]['id'])

#give this function a name of the cinema and it will give you the ID
#Example: get_id('5 Звезд на Новокузнецкой')


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

