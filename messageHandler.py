import vkapi
import os
import importlib
import sqlite3
import datetime
from command_system import command_list
from commands.chat import chat_user_new
from commands.chat import chat_message
from commands.congratulation import congratulation_new
from commands.congratulation import congratulation_message


# определение погрешности(ошибок) в сообщении пользователя
def damerau_levenshtein_distance(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1, lenstr1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2 + 1):
        d[(-1, j)] = j + 1
    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,
                d[(i, j - 1)] + 1,
                d[(i - 1, j - 1)] + cost,
            )
            if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)  # transposition
    return d[lenstr1 - 1, lenstr2 - 1]


# определение списка команд в папке commands, и фильтр .py
def load_modules():
    files = os.listdir("mysite/commands")
    modules = filter(lambda x: x.endswith('.py'), files)
    for m in modules:
        importlib.import_module("commands." + m[0:-3])


# ответ пользователю, при запросе команды
def get_answer(body_s, user_id, token, acces_commands):
    body = body_s.split(' ')[0]
    message = "Прости, я бот, не понимаю тебя. Напиши 'помощь', чтобы узнать мои команды"
    attachment = ''
    distance = len(body)
    command = None
    key = ''
    for c in command_list:
        if c.access in acces_commands:
            for k in c.keys:
                d = damerau_levenshtein_distance(body, k)
                if d < distance:
                    distance = d
                    command = c
                    key = k
                    if distance == 0:
                        message, attachment = c.process(user_id, token, acces_commands, body_s)
                        return message, attachment
        if distance < len(body) * 0.4:
            message, attachment = command.process(user_id, token, acces_commands, body_s)
            message = 'Я понял ваш запрос как "%s"\n\n' % key + message
    return message, attachment


# сообщение пользователю, когда он пытается написать боту не подписавшись
def create_answer(data, token, acces_commands, group_id, groups_link):
    user_id = data['user_id']
    if chat_user_new('result', token, user_id):  # проверка, является ли юзер участником чата
        user_id, message, attachment = chat_message(data['user_id'], data, token)
        vkapi.send_message(user_id, token, message, attachment)
    elif congratulation_new(token, user_id, 'result'):  # проверка юзера на отправку поздравления другу
        attachment = ''
        message = congratulation_message(token, user_id, 'test id', data, group_id)
        vkapi.send_message(user_id, token, message, attachment)
    else:  # проверка юзера, является ли участником группы
        groups_friend = vkapi.groups_isMember(user_id, token, group_id)
        if groups_friend == 1:
            time_black = black_list(user_id)
            if time_black:  # проверка на черный список
                message = 'Вы в черном списке ещё на ' + str(time_black)
                attachment = ''
                vkapi.send_message(user_id, token, message, attachment)
            else:
                load_modules()
                message, attachment = get_answer(data['body'].lower(), user_id, token, acces_commands)
                vkapi.send_message(user_id, token, message, attachment)
        else:
            message = "Для работы с ботом нужно быть подписчиком сообщества: " + groups_link
            vkapi.send_message(user_id, token, message)


# сообщение пользователю, когда он подписывается
def create_new_user(data, token, acces_commands, group_id):
    if 'create_new_user' in acces_commands:
        if vkapi.message_resolution(data['user_id'], group_id, token) == 1:
            user_id = data['user_id']
            data_user = vkapi.get_users(user_id)
            message = data_user[0][
                          'first_name'] + ', ' + "благодарю Вас за подписку. Напишите 'помощь' для работы с ботом сообщества."
            vkapi.send_message(user_id, token, message)


# сообщение пользователю, когда он отписывается
def create_delete_user(data, token, acces_commands, group_id):
    if 'create_delete_user' in acces_commands:
        if vkapi.message_resolution(data['user_id'], group_id, token) == 1:
            user_id = data['user_id']
            message = "Надеюсь, я был тебе полезен, возвращайся, когда ещё будет нужна моя помощь."
            vkapi.send_message(user_id, token, message)


# сообщение пользователю, когда он делает репост
def wall_repost(data, token, acces_commands, group_id):
    if 'wall_repost' in acces_commands:
        if data['owner_id'] > 0:
            if vkapi.message_resolution(data['owner_id'], group_id, token) == 1:
                user_id = data['owner_id']
                message = "Спасибо, что поделились новостью. "
                vkapi.send_message(user_id, token, message)


# проверка на вхождение в черный список
def black_list(user_id):
    con = sqlite3.connect('mysite/black_list.db')
    cur = con.cursor()
    cur.execute(
        "SELECT id_users_black,recording_date,expiration_date,quantity FROM black_users WHERE id_users_black={id}".format(
            id=user_id))
    result = cur.fetchone()
    if result:
        recording_date = datetime.datetime.today()
        expiration_date = datetime.datetime.strptime(result[2].split('.')[0], "%Y-%m-%d %H:%M:%S")
        if expiration_date > recording_date:
            time_black = str(expiration_date - recording_date).split('.')[0]
            return time_black
        cur.close()
        con.close()
    else:
        cur.close()
        con.close()
        return False
