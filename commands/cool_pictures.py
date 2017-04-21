import command_system
import vkapi


def cool_pictures():
    attachment = vkapi.get_random_wall_picture(-42564857)
    message = 'Вот тебе картинка :)\nВ следующий раз я пришлю другую.'
    return message, attachment


cat_command = command_system.Command()

cat_command.keys = ['фото', 'foto']
cat_command.description = 'Пришлю красивую картинку'
cat_command.process = cool_pictures
