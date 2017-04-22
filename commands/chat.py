import command_system


def chat(user_id):
    message = 'Вы добавлены в очередь поиска, мы скоро найдем Вам собеседника.'
    return message, ''


chat_command = command_system.Command()

chat_command.keys = ['чат']
chat_command.description = 'Анонимный чат'
chat_command.process = chat

