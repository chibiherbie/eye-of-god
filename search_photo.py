import dlib
from scipy.spatial import distance  # для расчёта схожести
from skimage import io
import sqlite3
import requests
import shutil
import os


# global
face_descriptor_know = ''
process_bar = 0


def search_photo_db(photo, gender, add_search, ProgressBarThread):
    """алгоритм
    переадём путь фото
    переделываем его в нашу структуру
    сраниваем его евклидованое расстояние с другими
    выводим результат"""

    global face_descriptor_know
    global process_bar

    process_bar = float()
    name_table = 'users_woman'
    id_people = []

    # ищем дескприптер фотки пользователя
    face_descriptor_know = face_descriptor(photo)

    if any(face_descriptor_know):  # если лицо есть

        # подключаемся к бд
        con = sqlite3.connect('data/photo/vk_krasnoyarsk.db')
        cur = con.cursor()

        if gender == 2:
            name_table = 'users_man'

        # если есть доп проверка, то задаём нахождение 30% при первом поиске, остальные 70% выыделяем под доп
        num_for_progress = 30 if add_search else 100

        # print(name_table)

        count = 0  # переменная для постепенного взятия данных из бд
        for i in range(1000, 20001, 1000):
            process_bar += 1000 * num_for_progress / 20000  # подсчитываем прогресс

            # берём данные из бд
            face_descriptor_list = cur.execute(f'''SELECT * FROM {name_table} WHERE id BETWEEN ? and ?''',
                                               (count, i)).fetchall()
            count += 1000
            for n, elem in enumerate(face_descriptor_list):
                if elem[3] == 'null':
                    continue

                # проверка личности, есть ли она в бд
                # if str(elem[1]) == 'config.MY_ID':
                #     print(elem[2])

                data = elem[3].replace('[', '').split(']')  # раскрываем данные

                for num, face in enumerate(data):
                    if num > 0:
                        face = face[2:]
                        if not face:
                            continue

                    face = [float(i[:10]) for i in face.split(', ')]  # преобразуем дескриптер до нужного формата

                    # высчитываем евклидовое значение
                    if distance.euclidean(face_descriptor_know, face) < 0.56:
                        id_people.append((face_descriptor_list[n][:3],
                                          url_to_str(face_descriptor_list[n][4], num)))

            ProgressBarThread.progress.emit(process_bar)  # отправялем сигнал для обновление статус бара

        con.close()  # закрываем бд

        if id_people:  # если сходства есть
            print(len(set(id_people)), len(id_people))

            # если нет доп проверки, выдаём результат
            if not add_search:
                # пересобираем даныые для вывода
                for n, user in enumerate(id_people):
                    id_people[n] = (user[0][1], user[0][2], 'https://vk.com/id' + str(user[0][1]))

                ProgressBarThread.progress.emit(100)  # статус обработки
                return list(set(id_people))
            return rechecking_photo(list(set(id_people)), ProgressBarThread)  # если проверка есть
        else:
            print('ничего')
            return 'Не найдено сходств'
    else:
        print('не обнаружена лица')
        return 'Не обнаружена лица'


# преобразуем ссылку в нужный формат
def url_to_str(url, n):
    url = url.replace('[', '').replace(']', '').split(', ')
    return url[n].replace('"', '')


# доп проверка (DEMO)
def rechecking_photo(list_data, ProgressBarThread):
    global process_bar

    rechecking_user = []

    for user in list_data:
        process_bar += 70 / len(list_data)  # процент за одного пользавателя

        if user[1]:
            r = requests.get(user[1], stream=True)  # делаем запрос
            with open('pars_img/' + str(user[0][1]) + '.jpg', 'wb') as f:  # скачиваем фото
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

            face_descriptor_unknow = face_descriptor('pars_img/' + str(user[0][1]) + '.jpg')  # определяем дескриптер

            os.remove(f'pars_img/{str(user[0][1])}.jpg')  # удаяляем изображение

            # высчитываем евклидовое значение
            if distance.euclidean(face_descriptor_know, face_descriptor_unknow) < 0.54:
                rechecking_user.append((user[0][1], user[0][2], 'https://vk.com/id' + str(user[0][1])))

            ProgressBarThread.progress.emit(process_bar)  # статус обработки

    # print(len(set(rechecking_user)))

    if list_data:  # если при доп проверки все возможные люди исчезли, выводим предыдущий поиск
        return list(set(rechecking_user))
    return list_data


# поиск дескриптера лица
def face_descriptor(pic):
    # Для выделения на фото лица
    sp = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
    # для выделения дискриптеров
    facerec = dlib.face_recognition_model_v1('models/dlib_face_recognition_resnet_model_v1.dat')

    try:
        img = io.imread(pic)  # считываем картинку

        detector = dlib.get_frontal_face_detector()  # определяем лицо

        dets = detector(img, 1)  # рисуем фигуру лица

        if dets:
            # выводим картинку
            # win1 = dlib.image_window()
            # win1.set_image(img)

            for d in dets:
                shape = sp(img, d)  # находим черты лица

                # добовляем на картинку черты
                # win1.add_overlay(d)
                # win1.add_overlay(shape)

            # win1.wait_for_keypress('q')  # ожидаем выхода

            return facerec.compute_face_descriptor(img, shape)
        else:
            return ''

    except RuntimeError:  # если лицо не было найдено
        return ''


# print(search_photo_db('test_foto/3.jpg', 2))  # проверка файла