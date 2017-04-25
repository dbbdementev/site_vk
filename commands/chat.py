import command_system
import vkapi
from settings import *
import sqlite3


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
    elif data['body'].lower() == 'блять':  # исключаем маты
        record_black_users(user_id)
        message = 'Вам бан за мат'
        return user_id, message, ''
    else:  # отправка сообщения собеседнику
        if interlocutor(user_id):
            message = data['body']
            user_id_interlocutor = interlocutor(user_id)
            if 'attachments' in data:  # определяем наличие мультимедии
                if 'access_key' in data['attachments'][0][str(data['attachments'][0]['type'])]:
                    attachment = str(str(data['attachments'][0]['type']) +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])]['owner_id']) + '_' +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])]['id']) + '_' +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])]['access_key']))
                else:
                    attachment = str(str(data['attachments'][0]['type']) +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])]['owner_id']) + '_' +
                                     str(data['attachments'][0][str(data['attachments'][0]['type'])]['id']))
            else:
                attachment = ''
            return user_id_interlocutor, message, attachment
        else:  # если собеседник еще не найден, но юзер пишет
            message = "Подождите ещё немного или напишите 'стоп', чтобы закрыть чат."
            return user_id, message, ''

def record_black_users(user_id):
    con = sqlite3.connect('mysite/black_list.db')
    cur = con.cursor()
    cur.execute("INSERT INTO black_users(id_users_black) VALUES {user_id}".format(user_id=user_id))
    arr = cur.fetchall()[0]
    cur.close()
    con.close()
    return arr