import command_system
import vkapi
import time
import black_list


def congratulation(user_id, token, acces_commands, body):
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
                if black_list.words_black(data['body']):  # исключаем маты
                    message = black_list.record_black_users(user_id)
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
                    return 'Из-за ограничений, для сообществ вконтакте, я могу отправить сообщение только с разрешения.\n Этот пользователь ещё не разрешил отправлять ему сообщения.'
                elif message == 'code':
                    messages = birthday_group(token, group_id)
                    return messages
        else:
            message = test_ids(token, str(data['body']), group_id)
            if message == 'ok':
                congratulation_group_id = {user_id: data['body']}
                congratulation_users_id[token] = congratulation_group_id
                return 'Теперь можете написать поздравление. Отправлять можно только текст.'
            elif message == 'numeral':
                congratulation_new(token, user_id, 'delete')
                return 'id должен содержать только цифры'
            elif message == 'no':
                congratulation_new(token, user_id, 'delete')
                return 'Из-за ограничений, для сообществ вконтакте, я могу отправить сообщение только с разрешения.\n Этот пользователь ещё не разрешил отправлять ему сообщения.'
            elif message == 'code':
                messages = birthday_group(token, group_id)
                return messages
    return 'Отправлять можно только текст.Напишите ещё раз.'


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
    user = vkapi.birthday_users_groups(group_id)
    quantity_birthday = 0
    quantity_messages = 0
    message = 'Никаких сомнений быть не может:\n' \
              'День рожденья — лучший день в году!\n' \
              'Пусть он жизнь по полочкам разложит\n' \
              'И поставит счастье на виду!\n' \
              '\n' \
              'Ближе к счастью — мир, любовь, удачу,\n' \
              'Дружбу, доброту, надежду, веру.\n' \
              'Где-то рядом — дом, машину, дачу,\n' \
              'Деньги и успешную карьеру!\n' \
              '\n' \
              'Пусть судьба возьмет всё это вместе\n' \
              'И назначит жизни долгий срок,\n' \
              'Чтобы тебе жилось ещё лет двести\n' \
              'Без проблем, волнений и тревог!\n'
    users_id = ''
    for users in user['items']:
        if 'bdate' in users:
            if birth_day == int(users['bdate'].split('.')[0]) and birth_month == int(users['bdate'].split('.')[1]):
                quantity_birthday += 1
                if vkapi.message_resolution(users['id'], group_id, token) == 1:
                    users_id = users_id + str(users['id']) + ','
                    quantity_messages += 1
            else:
                continue
    if users_id:
        vkapi.send_messages(users_id, token, message, attachment="")
    message = 'Сегодня день рождения празднуют: ' + str(quantity_birthday) + ' человек. Я отправил ' + str(quantity_birthday) + ' поздравлений'
    return message
