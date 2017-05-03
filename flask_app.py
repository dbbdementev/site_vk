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
    if data['type'] == 'confirmation' and hashlib.md5(bytes(str(data['group_id']), 'cp1251')).hexdigest() in confirmation_token:
        return confirmation_token[hashlib.md5(bytes(str(data['group_id']), 'cp1251')).hexdigest()]
    if hashlib.md5(bytes(data['secret'], 'cp1251')).hexdigest() in token:
        secret = hashlib.md5(bytes(data['secret'], 'cp1251')).hexdigest()
        if data['type'] == 'message_new':
            messageHandler.create_answer(data['object'],
                                         token[secret],
                                         acces_commands[secret],
                                         data['group_id'],
                                         groups_link[secret])
            return 'ok'
        elif data['type'] == 'group_join':
            messageHandler.create_new_user(data['object'],
                                           token[secret],
                                           acces_commands[secret],
                                           data['group_id'])
            return 'ok'
        elif data['type'] == 'group_leave':
            messageHandler.create_delete_user(data['object'],
                                              token[secret],
                                              acces_commands[secret],
                                              data['group_id'])
            return 'ok'
        elif data['type'] == 'wall_repost':
            messageHandler.wall_repost(data['object'],
                                              token[secret],
                                              acces_commands[secret],
                                              data['group_id'])
            return 'ok'
        else:
            return 'ok'
    else:
        return 'ok\nnot secret'
