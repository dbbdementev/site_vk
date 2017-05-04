import command_system
import vkapi
import black_list


# новый участник чата
def chat(user_id, token, acces_commands, body):
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
            couple_user = [user_id]
            couple_user_all[token] = couple_user
        if len(couple_user_all[token]) == 2:
            dict_couple_users('new', couple_user_all[token], token)
            message = "Собеседник найден. Можете ему написать. Чтобы завершить беседу, напишите 'стоп'."
            attachment = ''
            vkapi.send_message(str(couple_user_all[token][0]), token, message, attachment)
            couple_user_all.pop(token)
            return "Собеседник найден. Можете ему написать. Чтобы завершить беседу, напишите 'стоп'."
        con = chat_user_new('chat statistics', token)
        return "Вы добавлены в очередь поиска, мы скоро найдем Вам собеседника.\nЧтобы закончить чат, напишите 'стоп'." \
               "\nВ чате " + str(con) + " человек. Нас мало в группе. Пригласите своих друзей."

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
    elif black_list.words_black(data['body']):  # исключаем маты
        message_id = black_list.record_black_users(user_id)
        if message_id == 'Вы добавлены в черный список.':
            if interlocutor(user_id, token):
                message = 'Ваш собеседник заблокирован. Напишите "чат" для поиска другого.'
                vkapi.send_message(interlocutor(user_id, token), token, message)
            closing_conversation('stop black', user_id, token)
        if interlocutor(user_id, token):  # отправляем сообщение собеседнику о предупреждении
            message = 'Ваш собеседник получил предупреждение.'
            vkapi.send_message(interlocutor(user_id, token), token, message)
        return user_id, message_id, ''
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
