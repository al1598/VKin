from vk_api.longpoll import VkEventType
from core import bot
from db import create_table, drop_table


def chat_bot():
    for event in bot.longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text.lower()
            user_id = event.user_id
            bot.user_info = bot.get_user_info(user_id)
            if request == 'привет':
                bot.message_send(user_id, f'Здравствуйте, {bot.get_name(user_id)}! \n'
                                          f' Наберите команду "поиск".\n'
                                          f' "далее" - следующий профиль, \n'
                                          f' "удалить"- удалить БД, \n'
                                          f' "стоп"- завершение просмотра профилей.')
            elif request == 'поиск':
                bot.get_age_of_user(user_id)
                bot.get_city(user_id)
                bot.searching_for_person(user_id)
                bot.show_person(
                    user_id)
            elif request == 'удалить':
                drop_table()
                create_table()
                bot.message_send(user_id,
                                 f'База данных очищена. Наберите "поиск.')
            elif request == 'далее':
                if bot.get_person_id(user_id) != 0:
                    bot.show_person(user_id)
                else:
                    bot.message_send(user_id, f'Сначала наберите "поиск"')
            elif request == 'стоп':
                bot.message_send(user_id, 'До свидания!')
                continue
            else:
                bot.message_send(user_id, f'Неизвестная команда. Наберите: \n'
                                          f' "поиск" - поиск людей, \n'
                                          f' "далее" - следующий профиль, \n'
                                          f' "стоп" - завершение просмотра профилей.')

chat_bot()
