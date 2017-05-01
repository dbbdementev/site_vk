import command_system


def info(user_id, token, acces_commands, body):
    message = ''
    for c in command_system.command_list:
        if c.access in acces_commands:
            message += c.keys[0] + ' - ' + c.description + '\n'
    return message, ''


info_command = command_system.Command()

info_command.keys = ['помощь', 'помоги', 'help']
info_command.description = 'покажу список команд'
info_command.process = info
info_command.access = 'info'
