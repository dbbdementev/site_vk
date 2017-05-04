import command_system
import vkapi
import json
import requests
import time


def weather(user_id, token, acces_commands, body):
    message = 'Что? ' + str(body)
    if len(body.split(' ')) == 2:
        if body.split(' ')[1]:
            city = transfer(body.split(' ')[1].lower())
            message = g(city)
        else:
            message = 'Нужно написать город'
    if len(body.split(' ')) == 1:
        id_city = vkapi.get_users(user_id)
        if 'city' in id_city[0]:
            message = str(g(id_city[0]['city']['title'].lower()))
        else:
            message = 'Ваш город в профиле не доступен.\nЧто бы посмотреть погоду в другом городе введите, например, следующий код: погода Москва.  '
    return message, ''


weather_command = command_system.Command()

weather_command.keys = ['погода']
weather_command.description = 'покажу погоду'
weather_command.process = weather
weather_command.access = 'weather'


def g(city):
    with open('mysite/commands/city.list.json', 'r', encoding='utf-8') as f:
        f = json.load(f)
        for i in range(54100):
            if f[i]['name'].lower() == city.lower():
                result = requests.get(
                    'http://api.openweathermap.org/data/2.5/weather?id={id}&lang=ru&units=metric&APPID=37dc4dc88a8c4bb5d4df66baae7377eb'.format(
                        id=f[i]['id']))
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
    return 'Я не нашел такой город.'


key = 'trnsl.1.1.20170504T093040Z.f44827537f2d58b7.10a6ba219e8c06f9acb7958c15eed15fadcded10'


def transfer(text):
    result = requests.get(
        'https://translate.yandex.net/api/v1.5/tr.json/translate?key={key}&text={text}&lang=en&'.format(key=key,
                                                                                                        text=text))
    if result.status_code == 200:
        res = result.json()
        return res['text'][0]
