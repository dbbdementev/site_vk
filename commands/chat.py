import command_system
import vkapi

token = 'c16521dbd31c34b3f0c9f6536546965b72507a482ba99e1922904f303f799d2c3b0c5a99f6c395b84a8f7'


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


couple_users = []


# обьединение 2 участников в беседу
def association_two_users(code, user_id):
    if code == 'new':
        couple_users.append(user_id)
        if len(couple_users) == 2:
            dict_couple_users('new', couple_users)
            message = "Собеседник найден. Можете ему написать. Чтобы завершить беседу, напишите 'стоп'."
            attachment = ''
            vkapi.send_message(str(couple_users[0]), token, message, attachment)
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


def interlocutor_delete(user_id_interlocutor):
    message = "Ваш собеседник закрыл беседу. Чтобы найти другого, напишите 'чат'."
    vkapi.send_message(user_id_interlocutor, token, message)


# отправка сообщения
def chat_message(user_id, body):
    if body.lower() == 'стоп':
        if interlocutor(user_id):
            chat_user_new('delete', interlocutor(user_id))
            interlocutor_delete(interlocutor(user_id))
            chat_user_new('delete', user_id)
            message = "Вы  закрыли беседу. Чтобы найти другого собеседника, напишите 'чат'."
            return user_id, message, ''
        chat_user_new('delete', user_id)
        message = "Вы  закрыли чат. Чтобы посмотреть команды, напишите 'помощь'."
        return user_id, message, ''
    else:
        if interlocutor(user_id):
            message = body
            user_id_interlocutor = interlocutor(user_id)
            return user_id_interlocutor, message, ''
        else:
            message = "Подождите ещё немного или напишите 'стоп', чтобы закрыть чат."
            return user_id, message, ''
