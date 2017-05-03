from pprint import pprint
import json
import requests
import time
import datetime


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


def g():
    y = translate('кемерово')
    with open('city.list.json', 'r', encoding='utf-8') as f:
        f = json.load(f)
        for i in range(54100):
            if f[i]['name'].lower() == y:
                print(f[i])
                result = requests.get(
                    'http://api.openweathermap.org/data/2.5/weather?id={id}&lang=ru&units=metric&APPID=37dc4dc88a8c4bb5d4df66baae7377eb'.format(
                        id=f[i]['id']))
                if result.status_code == 200:
                    res = result.json()
                    print(res)
                    print(datetime.datetime.fromtimestamp(res['dt']))
                    print(datetime.datetime.utcfromtimestamp(res['dt']))
                    print(datetime.datetime.utcnow())
                    city=(
                        'данные на ' + str(
                            time.strftime('%d.%m.%Y %H:%M', time.localtime(res['dt']))) + ' в городе: ' +
                        res['name'])
                    temperature=('температура: ' + str(res['main']['temp']) + ' гр.')
                    cloud_cover=('облачность: ' + str(res['weather'][0]['description'])+str(res['clouds']['all'])+ '%')
                    wind=('ветер: ' + str(res['wind']['speed']) + ' м/с ' + str(res['wind']['deg']))
                    pressure=('давление: ' + str(int(res['main']['pressure']) * 0.75) + ' мм рт.ст.')
                    humidity=('влажность: ' + str(res['main']['humidity']) + ' %')
                    sunrise=('восход: ' + str(time.strftime('%H:%M', time.localtime(res['sys']['sunrise']))))
                    sunset=('закат: ' + str(time.strftime('%H:%M', time.localtime(res['sys']['sunset']))))
                    return city+'\n'+temperature+'\n'+cloud_cover+'\n'+wind+'\n'+pressure+'\n'+humidity+'\n'+sunrise+'\n'+sunset



print(g())

