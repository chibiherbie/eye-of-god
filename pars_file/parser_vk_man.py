import requests
import json
import vk_api
import time
import os
import shutil
import sqlite3
import numpy as np

from search_photo import face_descriptor
import config

# global
url = []  # сохраняет ссылки


def pars_foto():
    global url
    # vk.messages.send(user_id=my_id, message='sds', random_id=0)

    # данные для парсинга
    age = 20  # возраст от и до людей которых надо спарсить
    age_max = 20
    city_number = 73  # Номер города
    gender = 2  # пол: 1 - девушки, 2 - парни

    # Перебор возрастов
    while age <= age_max:
        day = 1

        # Перебор дней рождения
        while day <= 31:
            # Пишем какую группу людей качаем
            print('Download ID: ' + str(age) + ' Возраст, день рожения ' + str(day))

            # Получаем 1000 юзеров - их id, аву и ФИО
            data_users = vk.users.search(count=1000,
                                         fields='id, photo_max_orig, has_photo, '
                                                'first_name, last_name',
                                         city=city_number,
                                         sex=gender,
                                         age_from=age,
                                         age_to=age,
                                         birth_day=day)

            # пишем информацию о кол-во людей
            print('Кол-во людей: ' + str(data_users['count']))
            # записываем всю информацию
            with open('../logs/logs_man.txt', 'w', encoding='utf8') as f:
                f.write(f'Возраст {str(age)}, День рожедния {str(day)}\n'
                        f'Кол-во людей: {str(data_users["count"])}\n')

            day += 1

            # перебираем каждогго юзера
            for item_users in data_users['items']:
                # есть ли фото на аве. также проверка из логов, если тако таой id в бд
                if item_users['has_photo'] == 1 and str(item_users['id']) not in file_id:  # есть фото на аве

                    with open('../logs/logs_man.txt', 'a', encoding='utf8') as f:
                        f.write(str(item_users['id']) + '\n')

                    if not item_users['is_closed']:  # закрыт ли профиль
                        data_descriptor = photos_id(int(item_users['id']))  # получаем описание 3 фото
                        users_add_db(int(item_users['id']),  item_users['first_name'] + ' ' + str(item_users['last_name']),
                                     data_descriptor)

                    # если закрыт, то качаем аватарку
                    else:
                        download_photo(item_users['photo_max_orig'], item_users['id'])  # качаем фото для анализа
                        data_descriptor = face_descriptor(f'../pars_img/{item_users["id"]}.jpg', '../')

                        os.remove(f'../pars_img/{item_users["id"]}.jpg')

                        if data_descriptor:
                            url = [item_users['photo_max_orig']]

                            users_add_db(int(item_users['id']),
                                         item_users['first_name'] + ' ' + str(item_users['last_name']),
                                         data_descriptor)
        age += 1


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
                # берём только фото определёного типа (оптимальный вариант по соотношению качества с размером)
                if str(size['type']) == 'r':

                    # скачиваем фото и передаем для анализа лица
                    photo = download_photo(str(size['url']), id)
                    descriptor = face_descriptor(photo, '../')

                    # удаляем фотку
                    os.remove(photo)

                    if descriptor:  # если лицо найдено, добовляем его и ссылку на фото
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
        with open('../pars_img/' + str(name) + '.jpg', 'wb') as f:
            time.sleep(0.5)  # ожидаем загрузки
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

        return f'../pars_img/{name}.jpg'  # возвращаем путь до фото

    except Exception as e:
        print(e)


# записываем данные в бд
def users_add_db(id_users, name, data):
    # подключаемся
    con = sqlite3.connect('../data/photo/vk_krasnoyarsk.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()

    cur.execute('''INSERT INTO users_man(id_user, name, data, url_foto) VALUES (?, ?, ?, ?)''',
                (id_users, name, json.dumps(np.array(data).tolist()),  json.dumps(np.array(url).tolist())))
    con.commit()
    con.close()


if __name__ == '__main__':
    vk_session = vk_api.VkApi(token=config.VK_TOKEN)
    vk = vk_session.get_api()

    # при ошибки берём id польователей, которых записывали до ошибки, чтобы потом проверять, есть ли они в бд
    with open('../logs/logs_man — копия.txt', 'r') as f:
        file_id = f.read().split('\n')

    pars_foto()

    print('Done!')