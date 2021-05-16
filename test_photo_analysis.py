import dlib
from scipy.spatial import distance  # для расчёт схожести
import cv2
from skimage import io

# загрузка обученых моделей
sp = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')  # Для выыделения на фото лица
facerec = dlib.face_recognition_model_v1('models/dlib_face_recognition_resnet_model_v1.dat')  # для выделения дискриптеров

detector = dlib.get_frontal_face_detector()

img = io.imread('test_foto/15.jpg')  # считываем картинку
dets = detector(img, 1)
print(dets)
a = str(dets[0])

# print(a[2:10])
# print(int(a[2:5]))
# print(int(a[7:10]))

cv2.putText(img, 'Roman', (int(a[2:5]), int(a[7:10]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)  # 480 850
# показывыаем фото
win1 = dlib.image_window()
win1.clear_overlay()
win1.set_image(img)

# находим лицо


for d in dets:

    shape = sp(img, d)  # находим черты лица

    a = cv2.putText(img, 'NAME', (100 + 10, 120 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (200, 200, 200), 2)

    win1.clear_overlay()
    win1.add_overlay(d)

    win1.add_overlay(shape)

# извлекаем дискриптер
face_descriptor1 = facerec.compute_face_descriptor(img, shape)

img = io.imread('test_foto/15.jpg')

# win1 = dlib.image_window()
# win1.clear_overlay()
# win1.set_image(img)
#
# win1.wait_for_keypress('q')
try:
    dets = detector(img, 1)
    if dets:
        print('лицо есть')

        print(dets)
        a = str(dets[0])

        for k, d in enumerate(dets):
            shape = sp(img, d)
            face_descriptor2 = facerec.compute_face_descriptor(img, shape)

            l = distance.euclidean(face_descriptor1, face_descriptor2)
            if l < 0.53:
                print('Это ты')
                cv2.putText(img, 'face', (int(a[2:5]), int(a[7:10]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255),
                            3)
                win1 = dlib.image_window()
                win1.clear_overlay()
                win1.set_image(img)
                win1.add_overlay(d)
                win1.add_overlay(shape)
                win1.wait_for_keypress('q')
            else:
                print('не ты')
                cv2.putText(img, 'face', (int(a[2:5]), int(a[7:10]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255),
                            3)
                win1 = dlib.image_window()
                win1.set_image(img)
                win1.add_overlay(d)
                win1.add_overlay(shape)
                win1.wait_for_keypress('q')

    else:
        print('ошибка')
except Exception as e:
    print(e)