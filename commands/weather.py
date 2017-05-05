import command_system
import vkapi
import json
import requests
import time
import sqlite3


def weather(user_id, token, acces_commands, body):
    message = 'Что? ' + str(body)
    if len(body.split(' ')) == 2:
        if body.split(' ')[1]:
            city_id = city_base_read(body.split(' ')[1].lower(), '')
            if city_id:
                message = g(city_id)
            else:
                city = transfer(body.split(' ')[1].lower())
                city_id = city_join_id(city)
                if city_id:
                    city_base_record(body.split(' ')[1].lower(), city.lower(), city_id)
                    message = g(city_id)
                else:
                    message = 'Я не нашел такой город.'
        else:
            message = 'Нужно написать город'
    if len(body.split(' ')) == 1:
        id_city = vkapi.get_users(user_id)
        if 'city' in id_city[0]:
            city_id = city_base_read('', id_city[0]['city']['title'].lower())
            if city_id:
                message = g(city_id)
            else:
                city_id = city_join_id(id_city[0]['city']['title'].lower())
                if city_id:
                    message = g(city_id)
        else:
            message = 'Ваш город в профиле не доступен.\nЧто бы посмотреть погоду в другом городе введите, например, следующий код: погода Москва.  '
    return message, ''


weather_command = command_system.Command()

weather_command.keys = ['погода']
weather_command.description = 'покажу погоду'
weather_command.process = weather
weather_command.access = 'weather'


def city_base_read(city_ru, city_en):
    con = sqlite3.connect('mysite/main.db')
    cur = con.cursor()
    cur.execute("SELECT city_id,inquiry FROM cities WHERE city_ru=? OR city_en=?", (city_ru, city_en))
    result = cur.fetchone()
    cur.close()
    con.close()
    if result:
        return result[0]


def city_base_record(city_ru, city_en, city_id):
    inquiry = 1
    con = sqlite3.connect('mysite/main.db')
    cur = con.cursor()
    cur.execute("""INSERT INTO cities(city_ru,city_en,city_id,inquiry) VALUES (?,?,?,?)""",
                (city_ru, city_en, city_id, inquiry))
    con.commit()
    cur.close()
    con.close()


def city_join_id(city):
    with open('mysite/commands/city.list.json', 'r', encoding='utf-8') as f:
        f = json.load(f)
        for i in range(54100):
            if f[i]['name'].lower() == city.lower():
                city_id = f[i]['id']
                return city_id


def g(id):
    result = requests.get(
        'http://api.openweathermap.org/data/2.5/weather?id={id}&lang=ru&units=metric&APPID=37dc4dc88a8c4bb5d4df66baae7377eb'.format(
            id=id))
    if result.status_code == 200:
        res = result.json()
        city = (
            'данные на ' + str(
                time.strftime('%d.%m.%Y', time.localtime(res['dt']))) + ' в городе ' +
            res['name'])
        temperature = ('температура: ' + str(res['main']['temp']) + ' °С')
        if 'wind' in res:
            if 'deg' in res['wind']:
                if 0 <= res['wind']['deg'] <= 22 or 338 <= res['wind']['deg'] <= 360:
                    direction = 'северный'
                elif 23 <= res['wind']['deg'] <= 67:
                    direction = 'северо-восточный'
                elif 68 <= res['wind']['deg'] <= 112:
                    direction = 'восточный'
                elif 113 <= res['wind']['deg'] <= 157:
                    direction = 'юго-восточный'
                elif 158 <= res['wind']['deg'] <= 202:
                    direction = 'южный'
                elif 203 <= res['wind']['deg'] <= 247:
                    direction = 'юго-западный'
                elif 248 <= res['wind']['deg'] <= 292:
                    direction = 'западный'
                elif 293 <= res['wind']['deg'] <= 337:
                    direction = 'северо-западный'
                else:
                    direction = ''
            else:
                direction = ''
            if 'speed' in res['wind']:
                forse = str(res['wind']['speed'])
            else:
                forse = ''
            wind = ('ветер: ' + forse + ' м/с  ' + direction)
        else:
            wind = ''
        humidity = ('влажность: ' + str(res['main']['humidity']) + ' %')
        pressure = ('давление: ' + str(int(res['main']['pressure']) * 0.75) + ' мм рт.ст.')
        cloud_cover = ('облачность: ' + str(res['weather'][0]['description']) + ' (' + str(res['clouds']['all']) + '%)')
        if 'visibility' in res:
            visibility = ('видимость: ' + str(res['visibility']) + ' м')
        else:
            visibility = ''
        # sunrise = ('^восход: ' + str(time.strftime('%H:%M', time.localtime(res['sys']['sunrise']))))
        # sunset = ('^закат: ' + str(time.strftime('%H:%M', time.localtime(res['sys']['sunset']))))
        return city + '\n' + temperature + '\n' + humidity + '\n' + wind + '\n' + pressure + '\n' + cloud_cover + '\n' + visibility


key = 'trnsl.1.1.20170504T093040Z.f44827537f2d58b7.10a6ba219e8c06f9acb7958c15eed15fadcded10'


def transfer(text):
    result = requests.get(
        'https://translate.yandex.net/api/v1.5/tr.json/translate?key={key}&text={text}&lang=en&'.format(key=key,
                                                                                                        text=text))
    if result.status_code == 200:
        res = result.json()
        return res['text'][0]
