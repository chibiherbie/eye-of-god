import requests
import json
import time
import os
import shutil
import sqlite3
import vk_api
import numpy as np

from search_photo import face_descriptor

url = []


def photos_id(id):
    global url

    try:
        # деалем запрос на 20 фото профиля
        request = vk.photos.getAll(owner_id=id,
                                   count=20,
                                   no_service_albums=0)

        count_photo_face = []  # хранится фото с найдеными лицами
        url = []

        for item in request['items']:
            for size in item['sizes']:
                # берём только фото определёного типа
                if str(size['type']) == 'r':

                    # скачиваем фото и передаем для анализа лица
                    photo = download_photo(str(size['url']), id)
                    descriptor = face_descriptor(photo)

                    # удаляем фотку
                    os.remove(photo)

                    if descriptor:  # если лицо найдено, добовляем его
                        count_photo_face.append(descriptor)
                        url.append(str(size['url']))
                        if len(count_photo_face) == 3:  # набираем три фотографии
                            return count_photo_face

        if count_photo_face:
            return count_photo_face

    except Exception as e:
        print(e)


# скачиваем фото по url
def download_photo(url, name):
    try:
        r = requests.get(url, stream=True)  # делаем запрос
        with open('pars_img/' + str(name) + '.jpg', 'wb') as f:
            time.sleep(0.5)  # ожидаем загрузки
            r.raw.decode_content = True
            time.sleep(0.3)  # ожидаем загрузки
            shutil.copyfileobj(r.raw, f)

        return f'pars_img/{name}.jpg'  # возвращаем путь до фото

    except Exception as e:
        print(e)


def private(id, name):
    global url
    # возраст от и до людей которых надо спарсить
    age = 17
    age_max = 17

    # Номер города
    city_number = 73

    # 1 - девушки, 2 - парни
    gender = 2

    # Пауза для API
    time.sleep(2)

    # Пишем какую группу людей качаем
    print(id, name)

    # Получаем 1000 юзеров - их id, аву и ФИО
    data_users = vk.users.search(count=1000,
                                 fields='id, photo_max_orig,',
                                 city=city_number,
                                 sex=gender,
                                 age_from=age,
                                 age_to=age,
                                 q=name)

    # записываем информацию о кол-во людей
    print('Кол-во людей: ' + str(data_users['count']))

    for item_users in data_users['items']:
        if item_users['id'] == id:
            url = [item_users['photo_max_orig']]


vk_token = '434618c88aa75255b944f8d4d2a8578823a9fc47c5748accd90b68e0a7a15a087d3e431d3aefef6139914'

vk_session = vk_api.VkApi(token=vk_token)
vk = vk_session.get_api()

con = sqlite3.connect('data/photo/vk_krasnoyarsk.db')
cur = con.cursor()

count = 0

list_man = cur.execute('''SELECT * FROM users_man WHERE id < 5322''').fetchall()

for em in list_man:  # если
    if em[4] == '[]' and em[3] != 'null':
        private(em[1], em[2])

        cur.execute('''UPDATE users_man SET url_foto = ? WHERE id = ?''',
                    (json.dumps(np.array(url).tolist()), em[0]))
        con.commit()
    elif em[4] != '[]':  # если неправильная ссылка
        url_db = em[4].replace('[', '').replace(']', '').split(', ')
        for i in url_db:
            if str(em[1]) in i:
                private(em[1], em[2])

                cur.execute('''UPDATE users_man SET url_foto = ? WHERE id = ?''',
                            (json.dumps(np.array(url).tolist()), em[0]))
                con.commit()

con.close()

