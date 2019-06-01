# DON'T FORGET TO IMPORT 'requests' library
import requests

# functions for requests

with open('apikey.txt') as f:
    key = f.read()


def search_movies(id):
    URL = 'https://api.kinohod.ru/api/rest/site/v1/movies'
    PARAMS = {
        'apikey':key,
        'id':id
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    return data

# Example: id = 23211
# print(search_movies(23211))

# Vova: I changed the return of def below so that it fits the bot messages


def search_current_movies():
    URL = 'https://api.kinohod.ru/api/rest/site/v1/movies/recommend'
    PARAMS = {
        'apikey':key
    }
    r = requests.get(url=URL,params=PARAMS)
    data = r.json()
    data_new = []
    for i in range(5):
        data_new += [[f'{i+1}: ', data[i]["originalTitle"], 'IMDB rating:', data[i]["imdb_rating"]]]
    return data_new


def nearest_cinemas():
    URL = 'https://api.kinohod.ru/api/rest/site/v1/cinemas'
    PARAMS = {
        'apikey':key,
        'sort':5000,
        'city':1,
        'title':"Кинотеатр «5 Звезд на Павелецкой»",
        'timeBeforeSeance':60,
        'latitude':55.921336,
        'longitude':37.991876
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
    for i in range((len(data)) - 1):
        for j in range((len(data[i]['genres']) - 1)):
            if data[i]['genres'][j]['name'] == ganre:
                print(data[i]['originalTitle'])

# search_new_by_genres('экшен') there are around 30 ganres
