import command_system
import vkapi
import json
import requests
import time


def weather(user_id, token, acces_commands, body):
    message = 'Что? ' + str(body)
    if len(body.split(' ')) == 2:
        if body.split(' ')[1]:
            mes = translate(body.split(' ')[1].lower())
            message = g(mes)
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


def g(y):
    with open('mysite/commands/city.list.json', 'r', encoding='utf-8') as f:
        f = json.load(f)
        for i in range(54100):
            if f[i]['name'].lower() == y:
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
                    wind = ('ветер: ' + str(res['wind']['speed']) + ' м/с  ' + direction)
                    humidity = ('влажность: ' + str(res['main']['humidity']) + ' %')
                    pressure = ('давление: ' + str(int(res['main']['pressure']) * 0.75) + ' мм рт.ст.')
                    cloud_cover = ('облачность: ' + str(res['weather'][0]['description']) + ' (' + str(res['clouds']['all']) + '%)')
                    visibility = ('видимость: ' + str(res['visibility']) + ' м')
                    # sunrise = ('^восход: ' + str(time.strftime('%H:%M', time.localtime(res['sys']['sunrise']))))
                    # sunset = ('^закат: ' + str(time.strftime('%H:%M', time.localtime(res['sys']['sunset']))))
                    return city + '\n' + temperature + '\n' + humidity + '\n' + wind + '\n' + pressure + '\n' + cloud_cover + '\n' + visibility
    return 'Я не нашел такой город.'


def translate(name_translate):
    transtable = (
        ("а", "a"),
        ("б", "b"),
        ("в", "v"),
        ("г", "g"),
        ("д", "d"),
        ("е", "e"),
        ("ё", "yo"),
        ("ж", "zh"),
        ("з", "z"),
        ("и", "i"),
        ("й", "j"),
        ("к", "k"),
        ("л", "l"),
        ("м", "m"),
        ("н", "n"),
        ("о", "o"),
        ("п", "p"),
        ("р", "r"),
        ("с", "s"),
        ("т", "t"),
        ("у", "u"),
        ("ф", "f"),
        ("х", "h"),
        ("ц", "ts"),
        ("ч", "ch"),
        ("ш", "sh"),
        ("щ", "sch"),
        ("ъ", "`"),
        ("ы", "yi"),
        ("ь", "'"),
        ("э", "e"),
        ("ю", "y"),
        ("я", "ya"),
    )
    for symb_in, symb_out in transtable:
        name_translate = name_translate.replace(symb_in, symb_out)
    return name_translate
