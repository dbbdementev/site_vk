import command_system
import vkapi


def cool_pictures(user_id):
    attachment = vkapi.get_random_wall_picture(-42564857)
    message = 'Вот тебе картинка :)\nВ следующий раз я пришлю другую.'
    return message, attachment


cool_pictures_command = command_system.Command()

cool_pictures_command.keys = ['фото', 'foto']
cool_pictures_command.description = 'Пришлю красивую картинку'
cool_pictures_command.process = cool_pictures
