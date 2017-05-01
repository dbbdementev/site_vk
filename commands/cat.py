import command_system
import vkapi


def cat(user_id, token, acces_commands, body):
    attachment = vkapi.get_random_wall_picture(-32015300)
    message = 'Вот тебе котик :)\nВ следующий раз я пришлю другого котика.'
    return message, attachment


cat_command = command_system.Command()

cat_command.keys = ['котик', 'кошка', 'кот', 'котенок', 'котяра', 'cat']
cat_command.description = 'пришлю котика'
cat_command.process = cat
cat_command.access = 'cat'
