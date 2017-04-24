from flask import Flask, request, json
from settings import *
import messageHandler

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Привет, незнакомец !'


@app.route('/', methods=['POST'])
def processing():
    data = json.loads(request.data)
    if 'type' not in data.keys():
        return 'not vk'
    if data['type'] == 'confirmation' and data['group_id'] in confirmation_token:
        return confirmation_token[data['group_id']]
    if data['secret'] in token:
        if data['type'] == 'message_new':
            messageHandler.create_answer(data['object'],
                                         token[data['secret']],
                                         acces_commands[data['secret']],
                                         groups_id[data['secret']],
                                         groups_link[data['secret']])
            return 'ok'
        elif data['type'] == 'group_join':
            messageHandler.create_new_user(data['object'],
                                           token[data['secret']],
                                           acces_commands[data['secret']])
            return 'ok'
        elif data['type'] == 'group_leave':
            messageHandler.create_delete_user(data['object'],
                                              token[data['secret']],
                                              acces_commands[data['secret']])
            return 'ok'
        else:
            return 'There is no such type of event'
    else:
        return 'not secret'
