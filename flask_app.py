from flask import Flask, request, json
from settings import *
import messageHandler
import hashlib

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Привет, незнакомец !'


@app.route('/', methods=['POST'])
def processing():
    data = json.loads(request.data)
    if 'type' not in data.keys():
        return 'not vk'
    if data['type'] == 'confirmation' and register_group(hashlib.md5(bytes(str(data['group_id']), 'cp1251')).hexdigest()):
        return register_group(hashlib.md5(bytes(str(data['group_id']), 'cp1251')).hexdigest())
    main_group = main_groups(hashlib.md5(bytes(data['secret'], 'cp1251')).hexdigest())
    if main_group:
        if data['type'] == 'message_new':
            messageHandler.create_answer(data['object'],
                                         main_group[0],
                                         main_group[1],
                                         data['group_id'],
                                         main_group[2])
            return 'ok'
        elif data['type'] == 'group_join':
            messageHandler.create_new_user(data['object'],
                                           main_group[0],
                                           main_group[1],
                                           data['group_id'])
            return 'ok'
        elif data['type'] == 'group_leave':
            messageHandler.create_delete_user(data['object'],
                                              main_group[0],
                                              main_group[1],
                                              data['group_id'])
            return 'ok'
        elif data['type'] == 'wall_repost':
            messageHandler.wall_repost(data['object'],
                                       main_group[0],
                                       main_group[1],
                                       data['group_id'])
            return 'ok'
        else:
            return 'ok'
    else:
        return 'ok\nnot secret'
