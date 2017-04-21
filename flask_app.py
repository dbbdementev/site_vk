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
    if data['secret'] in token:
        if data['type'] == 'confirmation':
            return confirmation_token[data['secret']]
        elif data['type'] == 'message_new':
            messageHandler.create_answer(data['object'], token[data['secret']])
            return 'ok'
        elif data['type'] == 'group_join':
            messageHandler.create_new_user(data['object'], token[data['secret']])
            return 'ok'
        elif data['type'] == 'group_leave':
            messageHandler.create_delete_user(data['object'], token[data['secret']])
            return 'ok'
    else:
        return 'not secret'
