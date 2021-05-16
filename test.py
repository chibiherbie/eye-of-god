
# from config import yandex_api
# import requests
#
# pos = 'https://geocode-maps.yandex.ru/1.x/?apikey=' + yandex_api +'&geocode=Тверская+6'
#
# r = requests.get(pos)
#
# print(r)


#
# import sys
# from io import BytesIO
# from config import yandex_api
# # Этот класс поможет нам сделать картинку из потока байт
#
# import requests
# from PIL import Image
#
#
# def get_object_size(geo_object):
#     lower_corner = list(map(float, geo_object['boundedBy']['Envelope']['lowerCorner'].split()))
#     upper_corner = list(map(float, geo_object['boundedBy']['Envelope']['upperCorner'].split()))
#     return (str(abs(lower_corner[0] - upper_corner[0]) / 2),
#             str(abs(lower_corner[1] - upper_corner[1]) / 2))
#
#
# # Пусть наше приложение предполагает запуск:
# # python search.py Москва, ул. Ак. Королева, 12
# # Тогда запрос к геокодеру формируется следующим образом:
# toponym_to_find = "Красноярск молоова 28"
#
# geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
#
# geocoder_params = {
#     "apikey": yandex_api,
#     "geocode": toponym_to_find,
#     "format": "json"}
#
# response = requests.get(geocoder_api_server, params=geocoder_params)
#
# if not response:
#     # обработка ошибочной ситуации
#     pass
#
# # Преобразуем ответ в json-объект
# json_response = response.json()
#
# # Получаем первый топоним из ответа геокодера.
# toponym = json_response["response"]["GeoObjectCollection"][
#     "featureMember"][0]["GeoObject"]
#
# # Координаты центра топонима:
# toponym_coodrinates = toponym["Point"]["pos"]
#
# # Долгота и широта:
# toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
#
# delta = get_object_size(toponym)
#
# # Собираем параметры для запроса к StaticMapsAPI:
# map_params = {
#     'll': ','.join([toponym_longitude, toponym_lattitude]),
#     'spn': ",".join([delta[0], delta[1]]),
#     'l': 'map',
#     'pt': ','.join([toponym_longitude, toponym_lattitude, 'org'])
# }
#
# map_api_server = "http://static-maps.yandex.ru/1.x/"
#
# # ... и выполняем запрос
# response = requests.get(map_api_server, params=map_params)
#
# Image.open(BytesIO(
#     response.content)).show()
# # Создадим картинку
# # и тут же ее покажем встроенным просмотрщиком операционной системы


# import requests
# import urllib.request
# import json
#
# p = urllib.request.urlopen('https://rest-app.net/api/ads?login=bekkerrdm@gmail.com&token=4ff152c5654e660665341d625d1e8454&category_id=name=Роман')
# p = json.load(p)
#
# print(p)

# import asyncio
#
# TOKEN_POLICE = '1193203274:AAHMgeJdeg8ptnC3DI8M-1B_Tsv48r6FLos'  # police_xXgameXx_bot - название бота
#
# from aiogram import Bot, Dispatcher, executor, types
# import logging
#
# logging.basicConfig(level=logging.INFO)
#
# bot = Bot(token=TOKEN_POLICE)
# dp = Dispatcher(bot)
#
#
# @dp.message_handler()
# async def back(message: types.message):
#     print(message)
#
#
# async def start(m):
#     await bot.send_message('787316078', m)
#
#
# def send_number(phone):
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(start(phone))
#
#
# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)


import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll
import random
import config

TOKEN = 'b112dcb9a83b06861a748a1469f2ed660929dc66edbe2b3be2fc89893a80616cf953665040ec90f81385d'

def main():
    vk_session = vk_api.VkApi(
        token=TOKEN)


    vk = vk_session.get_api()
    vk.messages.send(user_id=config.MY_ID,
                     message="Спасибо, что написали нам. Мы обязательно ответим",
                     random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()