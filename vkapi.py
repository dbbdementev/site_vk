import vk
import random

session = vk.Session()
api = vk.API(session, v=5.63)


# отправка случайной фотографии в сообщении
def get_random_wall_picture(group_id):
    max_num = api.photos.get(owner_id=group_id, album_id='wall', count=0)['count']
    num = random.randint(1, max_num)
    photo = api.photos.get(owner_id=str(group_id), album_id='wall', count=1, offset=num)['items'][0]['id']
    attachment = 'photo' + str(group_id) + '_' + str(photo)
    return attachment


# сообщение пользователю
def send_message(user_id, token, message, attachment=""):
    api.messages.send(access_token=token, user_id=str(user_id), message=message, attachment=attachment)


# сообщение отправляется нескольким пользователям
def send_messages(user_id, token, message, attachment=""):
    api.messages.send(access_token=token, user_ids=str(user_id), message=message, attachment=attachment)


# запрос, о том состоит пользователь в группе или нет
def groups_isMember(user_id, token, group_id):
    groups_friend = api.groups.isMember(access_token=token, user_id=str(user_id), group_id=group_id)
    return groups_friend


# запрос данных о пользователе, без токена( с токеном общества не работает)
def get_users(user_id):
    data_user = api.users.get(user_id=str(user_id), fields='first_name')
    return data_user
