from pprint import pprint
import json
import requests
import time
import datetime

key='trnsl.1.1.20170504T093040Z.f44827537f2d58b7.10a6ba219e8c06f9acb7958c15eed15fadcded10'
def transfer(text):
    result = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate?key={key}&text={text}&lang=en&'.format(key=key,text=text))

    if result.status_code == 200:
        res = result.json()
        print(res['text'][0])
        return res['text'][0]


def g():
    y = transfer('бердск').lower()
    with open('city.list.json', 'r', encoding='utf-8') as f:
        f = json.load(f)
        for i in range(100000):
            if f[i]['name'].lower() == y:
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

