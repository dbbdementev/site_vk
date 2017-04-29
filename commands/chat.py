import command_system
import vkapi
from settings import *
import sqlite3
import datetime
from difflib import SequenceMatcher


# новый участник чата
def chat(user_id, token, acces_commands):
    message = chat_user_new('new', token, user_id)
    return message, ''


chat_command = command_system.Command()

chat_command.keys = ['чат']
chat_command.description = 'анонимный чат'
chat_command.process = chat
chat_command.access = 'chat'

chat_users_all = {}


# создание списка всех участников чата
def chat_user_new(code, token, user_id=''):
    if user_id:
        if code == 'new':
            if token in chat_users_all:
                chat_users_group = chat_users_all[token]
            else:
                chat_users_group = []
            chat_users_group.append(user_id)
            chat_users_all[token] = chat_users_group
            message = association_two_users('new', user_id, token)
            return message
        elif code == 'delete':
            if token in chat_users_all:
                chat_users_group = chat_users_all[token]
                chat_users_group.remove(user_id)
                chat_users_all[token] = chat_users_group
                dict_couple_users('delete', user_id, token)
                association_two_users('delete', user_id, token)
    if code == 'result':
        if token in chat_users_all:
            if user_id in chat_users_all[token]:
                return True
        return False
    if code == 'chat statistics':
        if token in chat_users_all:
            return len(chat_users_all[token])


couple_user_all = {}


# обьединение 2 участников в беседу
def association_two_users(code, user_id, token):
    if code == 'new':
        if token in couple_user_all:
            couple_user = couple_user_all[token]
            couple_user.append(user_id)
            couple_user_all[token] = couple_user
        else:
            couple_user = []
            couple_user.append(user_id)
            couple_user_all[token] = couple_user
        if len(couple_user_all[token]) == 2:
            dict_couple_users('new', couple_user_all[token], token)
            message = "Собеседник найден. Можете ему написать. Чтобы завершить беседу, напишите 'стоп'."
            attachment = ''
            vkapi.send_message(str(couple_user_all[token][0]), token, message, attachment)
            couple_user_all.pop(token)
            return "Собеседник найден. Можете ему написать. Чтобы завершить беседу, напишите 'стоп'."
        return "Вы добавлены в очередь поиска, мы скоро найдем Вам собеседника. Чтобы закончить чат, напишите 'стоп'."
    if code == 'delete':
        if token in couple_user_all:
            couple_user = couple_user_all[token]
            couple_user.remove(user_id)
            couple_user_all[token] = couple_user


couple_users_group = {}
couple_users_all = {}


# полный список пар участников
def dict_couple_users(code, list, token):
    if code == 'new':
        couple_users_group[list[1]] = list[0]
        couple_users_group[list[0]] = list[1]
        couple_users_all[token] = couple_users_group
    if code == 'delete':
        if token in couple_users_all:
            if list in couple_users_all[token]:
                del couple_users_all[token][list]
    if code == 'result':
        if token in couple_users_all:
            return couple_users_all[token]
        return False


# определение id собеседника
def interlocutor(user_id, token):
    user_id_interlocutor = dict_couple_users('result', '', token)
    if user_id_interlocutor:
        if user_id in user_id_interlocutor:
            return user_id_interlocutor[user_id]


# закрытие беседы
def closing_conversation(code, user_id, token):
    if code == 'stop':
        if interlocutor(user_id, token):
            chat_user_new('delete', token, interlocutor(user_id, token))
            message = "Ваш собеседник закрыл беседу. Чтобы найти другого, напишите 'чат'."
            vkapi.send_message(interlocutor(user_id, token), token, message)
            chat_user_new('delete', token, user_id)
            message = "Вы  закрыли беседу. Чтобы найти другого собеседника, напишите 'чат'."
            return message
        chat_user_new('delete', token, user_id)
        message = "Вы  закрыли чат. Чтобы посмотреть команды, напишите 'помощь'."
        return message
    if code == 'stop black':
        if interlocutor(user_id, token):
            chat_user_new('delete', token, interlocutor(user_id, token))
        chat_user_new('delete', token, user_id)


# отправка сообщения
def chat_message(user_id, data, token=''):
    if data['body'].lower() == 'стоп':
        message = closing_conversation('stop', user_id, token)
        return user_id, message, ''
    elif data['body'].lower() == '!статистика':
        message = 'В чате: ' + str(chat_user_new('chat statistics', token)) + ' человек'
        return user_id, message, ''
    elif words_black(data['body']):  # исключаем маты
        message = record_black_users(user_id)
        if interlocutor(user_id, token):  # отправляем сообщение собеседнику о предупреждении
            message = 'Ваш собеседник получил предупреждение.'
            vkapi.send_message(interlocutor(user_id, token), token, message)
        return user_id, message, ''
    else:  # отправка сообщения собеседнику
        if interlocutor(user_id, token):
            message = data['body']
            user_id_interlocutor = interlocutor(user_id, token)
            if 'attachments' in data:  # определяем наличие мультимедии
                if 'access_key' in data['attachments'][0][str(data['attachments'][0]['type'])]:
                    attachment = str(str(data['attachments'][0]['type']) +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])]
                                         ['owner_id']) + '_' +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])]['id']) + '_' +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])]['access_key']))
                else:
                    attachment = str(str(data['attachments'][0]['type']) +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])]
                                         ['owner_id']) + '_' +
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
            closing_conversation('stop_black', user_id, '')
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


# определение запрещенных слов
def words_black(text):
    words = text.lower().split(' ')
    words_list = ['блять', 'сиськи', 'пизда', 'нахуй', 'хуй', 'писю', 'пенис', 'ебланка', 'голой', 'трахну', 'член',
                  'пошлую', 'ебланище', 'пизда', 'гавно', 'срать', 'долбаеб', 'вагина', 'сукина', 'дебил', 'киску',
                  'выебу', 'суки', 'пиздуй', 'попа', 'спидом', 'мразь', 'кит', 'шмара', 'вирус', 'минет', 'хуя', 'ебал',
                  'мразь', 'шлюха', 'пошленькая', 'интим', 'шкура', 'пиздень', 'сосешь', 'схуяли', 'жопа', 'педофила',
                  'пидор', 'урод', 'дебил', 'даун', 'тити', 'титюльки', 'транс', 'трахнуть', 'шавуха', 'грудь', 'гей',
                  'куни', 'пидаром', 'девственницу', 'куратор', 'умрешь', 'кишки', 'вырежу', 'губой', 'ебаный', 'лох',
                  'вирт', 'ебальник', 'хрен', 'отсосать', 'ебемся', 'секс', 'онанизм']
    for i in words:
        for w in words_list:
            name = SequenceMatcher(lambda x: x in ' ', i, w).ratio()
            if name > 0.7:
                return True
    return False
