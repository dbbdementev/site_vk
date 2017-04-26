import command_system
import vkapi
from settings import *
import sqlite3
import datetime
from difflib import SequenceMatcher


# новый участник чата
def chat(user_id):
    message = chat_user_new('new', user_id)
    return message, ''


chat_command = command_system.Command()

chat_command.keys = ['чат']
chat_command.description = 'Анонимный чат'
chat_command.process = chat

queue_user = []


# создание списка всех участников чата
def chat_user_new(code, user_id=''):
    if user_id:
        if code == 'new':
            queue_user.append(user_id)
            message = association_two_users('new', user_id)
            return message
        elif code == 'delete':
            queue_user.remove(user_id)
            dict_couple_users('delete', user_id)
            association_two_users('delete', user_id)
    if code == 'result':
        return queue_user
    if code == 'chat statistics':
        return len(queue_user)


couple_users = []


# обьединение 2 участников в беседу
def association_two_users(code, user_id):
    if code == 'new':
        couple_users.append(user_id)
        if len(couple_users) == 2:
            dict_couple_users('new', couple_users)
            '''
            требуется настроить отправку сообщения 2 собеседнику, при этом токен нужно с базы брать
            message = "Собеседник найден. Можете ему написать. Чтобы завершить беседу, напишите 'стоп'."
            attachment = ''
            vkapi.send_message(str(couple_users[0]), token['34173cb38f07f89ddbebc2ac9128303f'], message, attachment)
            '''
            couple_users.pop()
            couple_users.pop()
            return "Собеседник найден. Можете ему написать. Чтобы завершить беседу, напишите 'стоп'."
        return "Вы добавлены в очередь поиска, мы скоро найдем Вам собеседника. Чтобы закончить чат, напишите 'стоп'."
    if code == 'delete':
        if couple_users:
            couple_users.remove(user_id)


couple_users_all = {}


# полный список пар участников
def dict_couple_users(code, list):
    if code == 'new':
        couple_users_all[list[1]] = list[0]
        couple_users_all[list[0]] = list[1]
    if code == 'delete':
        if list in couple_users_all:
            del couple_users_all[list]
    if code == 'result':
        return couple_users_all


# определение id собеседника
def interlocutor(user_id):
    user_id_interlocutor = dict_couple_users('result', '')
    if user_id in user_id_interlocutor:
        return user_id_interlocutor[user_id]


def interlocutor_delete(user_id_interlocutor, token):
    message = "Ваш собеседник закрыл беседу. Чтобы найти другого, напишите 'чат'."
    vkapi.send_message(user_id_interlocutor, token, message)


# отправка сообщения
def chat_message(user_id, data, token):
    if data['body'].lower() == 'стоп':
        if interlocutor(user_id):
            chat_user_new('delete', interlocutor(user_id))
            interlocutor_delete(interlocutor(user_id), token)
            chat_user_new('delete', user_id)
            message = "Вы  закрыли беседу. Чтобы найти другого собеседника, напишите 'чат'."
            return user_id, message, ''
        chat_user_new('delete', user_id)
        message = "Вы  закрыли чат. Чтобы посмотреть команды, напишите 'помощь'."
        return user_id, message, ''
    elif data['body'].lower() == '!статистика':
        message = 'В чате: ' + str(chat_user_new('chat statistics')) + ' человек'
        return user_id, message, ''
    elif words_black(data['body']):  # исключаем маты
        message = record_black_users(user_id)
        return user_id, message, ''
    else:  # отправка сообщения собеседнику
        if interlocutor(user_id):
            message = data['body']
            user_id_interlocutor = interlocutor(user_id)
            if 'attachments' in data:  # определяем наличие мультимедии
                if 'access_key' in data['attachments'][0][str(data['attachments'][0]['type'])]:
                    attachment = str(str(data['attachments'][0]['type']) +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])][
                                             'owner_id']) + '_' +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])]['id']) + '_' +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])]['access_key']))
                else:
                    attachment = str(str(data['attachments'][0]['type']) +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])][
                                             'owner_id']) + '_' +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])]['id']))
            else:
                attachment = ''
            return user_id_interlocutor, message, attachment
        else:  # если собеседник еще не найден, но юзер пишет
            message = "Подождите ещё немного или напишите 'стоп', чтобы закрыть чат."
            return user_id, message, ''


# добавление в черный список
def record_black_users(user_id):
    con = sqlite3.connect('mysite/black_list.db', isolation_level=None)
    cur = con.cursor()
    recording_date = datetime.datetime.today()
    cur.execute("SELECT id_users_black,quantity,warning FROM black_users WHERE id_users_black={id}".format(id=user_id))
    result = cur.fetchall()
    if result:
        if result[0][2] == 0:
            warning = 1
            cur.execute("UPDATE black_users SET warning=? WHERE id_users_black=?", (warning, user_id))
            return 'Вам 1 предупреждение.'
        if result[0][2] == 1:
            warning = 2
            cur.execute("UPDATE black_users SET warning=? WHERE id_users_black=?", (warning, user_id))
            return 'Вам 2 предупреждение.'
        if result[0][2] == 2:
            warning = 0
            quantity = result[0][1] + 1
            expiration_date = recording_date + datetime.timedelta(hours=quantity)
            cur.execute(
                "UPDATE black_users SET recording_date=?,expiration_date=?,quantity=?,warning=? WHERE id_users_black=?",
                (recording_date, expiration_date, quantity, warning, user_id))
            return 'Вы добавлены в черный список.'
        cur.close()
        con.close()
    else:
        quantity = 0
        warning = 1
        expiration_date = recording_date
        cur.execute(
            "INSERT INTO black_users(id_users_black,recording_date,expiration_date,quantity,warning) VALUES (?,?,?,?,?)",
            (user_id, recording_date, expiration_date, quantity, warning))
        return 'Вам 1 предупреждение.'
    cur.close()
    con.close()


def words_black(text):
    words = text.lower().split(' ')
    words_list = ['блять', 'сиськи', 'пизды', 'нахуй', 'хуй', 'писю', 'пенис', 'ебланка', 'голой', 'трахну', 'член',
                  'пошлую', 'ебланище', 'пизда', 'гавно', 'срать', 'долбаеб', 'вагину', 'сукина', 'дебил', 'киску',
                  'выебу', 'суки', 'пиздуй', 'попы', 'спидом', 'мразь', 'кит', 'шмара', 'вирус', 'минет', 'хуя', 'ебал',
                  'мразь', 'шлюха', 'пошденькая', 'интим', 'шкура', 'пиздень', 'сосешь', 'схуяли', 'жопа', 'педофила',
                  'пидор', 'урод', 'дебил', 'даун', 'тити', 'титюльки', 'транс', 'трахнуть', 'шавуха', 'грудь', 'гей',
                  'куни', 'пидаром', 'девственницу', 'куратор', 'умрешь', 'кишки', 'вырежу', 'губой', 'ебаный', 'лох',
                  'вирт', 'ебальник', 'хрен', 'отсосать', 'ебемся', 'секс', 'онанизм']
    for i in words:
        for w in words_list:
            name = SequenceMatcher(lambda x: x in ' ', i, w).ratio()
            if name > 0.75:
                return True
    return False
