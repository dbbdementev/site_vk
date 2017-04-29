import command_system
import vkapi
import sqlite3
import datetime
from difflib import SequenceMatcher
import time


def congratulation(user_id, token, acces_commands):
    message = congratulation_new(token, user_id, 'new')
    return message, ''


congratulation_command = command_system.Command()

congratulation_command.keys = ['поздравь']
congratulation_command.description = 'поздравлю друга'
congratulation_command.process = congratulation
congratulation_command.access = 'congratulation'

congratulation_users_all = {}


# создаем список всех кто хочет поздравить друга
def congratulation_new(token, user_id, code):
    if code == 'new':
        if token in congratulation_users_all:
            congratulation_users_group = congratulation_users_all[token]
        else:
            congratulation_users_group = []
        congratulation_users_group.append(user_id)
        congratulation_users_all[token] = congratulation_users_group
        message = 'Напишите id вашего друга.'
        return message
    if code == 'result':
        if token in congratulation_users_all:
            if user_id in congratulation_users_all[token]:
                return True
        return False
    if code == 'delete':
        if token in congratulation_users_all:
            congratulation_users_group = congratulation_users_all[token]
            congratulation_users_group.remove(user_id)
            congratulation_users_all[token] = congratulation_users_group


congratulation_users_id = {}


def congratulation_message(token, user_id, code, data, group_id):
    if data['body']:
        if token in congratulation_users_id:
            if user_id in congratulation_users_id[token]:
                if words_black(data['body']):  # исключаем маты
                    message = record_black_users(user_id)
                    attachment = ''
                    del congratulation_users_id[token][user_id]
                    congratulation_new(token, user_id, 'delete')
                    return message
                else:
                    message = data['body']
                    attachment = ''
                    vkapi.send_message(congratulation_users_id[token][user_id], token, message, attachment)
                    del congratulation_users_id[token][user_id]
                    congratulation_new(token, user_id, 'delete')
                    return 'Ваше сообщение отправлено'
            else:
                message = test_ids(token, str(data['body']), group_id)
                if message == 'ok':
                    congratulation_users_id[token][user_id] = data['body']
                    return 'Теперь можете написать поздравление.'
                elif message == 'numeral':
                    congratulation_new(token, user_id, 'delete')
                    return 'id должен содержать только цифры'
                elif message == 'no':
                    congratulation_new(token, user_id, 'delete')
                    return 'Этот пользователь ещё не разрешил отправлять ему сообщения.'
                elif message == 'code':
                    messages = birthday_group(token, group_id)
                    return messages
        else:
            message = test_ids(token, str(data['body']), group_id)
            if message == 'ok':
                congratulation_group_id = {}
                congratulation_group_id[user_id] = data['body']
                congratulation_users_id[token] = congratulation_group_id
                return 'Теперь можете написать поздравление.'
            elif message == 'numeral':
                congratulation_new(token, user_id, 'delete')
                return 'id должен содержать только цифры'
            elif message == 'no':
                congratulation_new(token, user_id, 'delete')
                return 'Этот пользователь ещё не разрешил отправлять ему сообщения.'
            elif message == 'code':
                messages = birthday_group(token, group_id)
                return messages
    return 'Ваш друг запретил отправлять ему сообщения'


def test_ids(token, id, group_id):
    if id == '!сегодня день рождения':
        return 'code'
    if not id.isdigit():
        return 'numeral'
    else:
        if vkapi.message_resolution(id, group_id, token) == 0:
            return 'no'
        else:
            return 'ok'


def birthday_group(token, group_id):
    birth_day = time.localtime().tm_mday
    birth_month = time.localtime().tm_mon
    message = vkapi.birthday_users_groups(group_id)
    '''
    message_name = ''
    message_foto = ''
    for users in user['users']:
        if 'bdate' in users:
            if birth_day == int(users['bdate'].split('.')[0]) and birth_month == int(users['bdate'].split('.')[1]):
                message_name = message_name + users['first_name'] + ', '
            else:
                continue
    message = 'Поздравляем с Днем рождения участников группы:' + message_name + message_foto
    '''
    return message


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
            # closing_conversation('stop_black', user_id, '')
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
