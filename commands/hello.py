import command_system


def hello(user_id, token, acces_commands):
    message = 'Привет, друг!\nЯ новый чат-бот.'
    return message, ''


hello_command = command_system.Command()

hello_command.keys = ['привет', 'hello', 'дратути', 'здравствуй', 'здравствуйте']
hello_command.description = 'поприветствую тебя'
hello_command.process = hello
hello_command.access = 'hello'
