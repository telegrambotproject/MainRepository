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

    
def search_movies(movie_id):
    URL = 'https://api.kinohod.ru/api/rest/site/v1/movies'
    PARAMS = {
        'apikey':key,
        'id':movie_id
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    return data[0]['originalTitle'], data[0]['annotationFull'], data[0]['genres'][0]['name']

# Example: id = 23211
# print(search_movies(23211))

# Vova: I changed the return of def below so that it fits the bot messages


def search_current_movies(movie_number):  # кол-во фильмов
    URL = 'https://api.kinohod.ru/api/rest/site/v1/movies/recommend'
    PARAMS = {
        'apikey':key,
        'limit': movie_number
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    data_new = []
    for i in range(movie_number):
        data_new += [[data[i]["imdb_id"], f'{i+1}: ', data[i]["originalTitle"], 'IMDB rating:', data[i]["imdb_rating"]]]
    return data_new


def nearest_cinemas():
    URL = 'https://api.kinohod.ru/api/rest/site/v1/cinemas'
    PARAMS = {
        'apikey': key,
        'sort': 5000,
        'city': 1,
        'timeBeforeSeance':  60,
        'latitude': 55.921336,
        'longitude': 37.991876
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    for i in range(5):
        print(data[i]['shortTitle'], data[i]['mall'], data[i]['phones'][0]['number'])

# nearest_cinemas() latitude and longitude from the user
# in the input of the function


def movies_in_cinema(id):
    URL = f'https://api.kinohod.ru/api/rest/site/v1/cinemas/{id}/movies'
    URLname = f'https://api.kinohod.ru/api/rest/site/v1/cinemas/{id}'
    PARAMSname = {
        'apikey':key
    }
    PARAMS = {
        'apikey':key
    }
    rname = requests.get(url=URLname, params=PARAMSname)
    dataname = rname.json()
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    cinemaname = dataname['shortTitle']
    print(f'Movies in {cinemaname} are:')
    for i in range(5):
        print(data[i]["originalTitle"])

# movies_in_cinema(227)
# 227 = id of the particular cinema


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
        film_date = "3000-01-01"
        film_id = "False"
        for m in data['results']:  # Беру ближайший фильм из списка
            if now.strftime("%Y-%m-%d") < m['release_date'] and m['release_date'] < film_date:
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
            return data.get('imdb_id', [False]*3)[2:], data.get('original_title', False), film_date
        else:
            print(data)
            return False, None, None
    else:
        print(data)
        return False, None, None



