import telebot
import requests

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
              'travelmode': 'walking'}
    p = requests.Request('GET', url=url, params=params).prepare()
    print(p.url)
    waypoints.clear()
    waypoint_id.clear()
    return p.url


telebot.apihelper.proxy = {'https': 'https://188.152.158.252:8118'}
bot = telebot.TeleBot('846385082:AAHf9ZM9ulaRR0b79g9oBC1mRqCXaor6GiA')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'скинь боту свою геолокацию')


@bot.message_handler(content_types=['location'])
def handle_location(message):
    location[0] = f'{message.location.latitude}, {message.location.longitude}'
    bot.send_message(message.chat.id, "Напиши пару мест через запятую")
    bot.register_next_step_handler(message, get_place)


def get_place(message):
    places = message.text.split(',')
    for p in places:
        response = search(location[0], p, key)
        print(response['results'][0])
        lat = response['results'][0]['geometry']['location']['lat']
        lon = response['results'][0]['geometry']['location']['lng']
        bot.send_message(message.chat.id, response['results'][0]['name'])
        waypoints.append(f'{lat}, {lon}')
        waypoint_id.append(response['results'][0]['place_id'])
    m = route(location[0], waypoints, waypoint_id, location[0])

    bot.send_message(message.chat.id, m)




bot.polling()
