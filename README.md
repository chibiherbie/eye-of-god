
# Eye of god

#### _Этот проект создан для поиска людей по информации: номер телефона, фотография человека, email и ФИО_

### Номер телефона
По номеру можно узнать регион, оператора и страну
_В разработке находится поиск его имени или псевдонима. Также социальные сети: Вк, Facebook, instagram_

### Email
По email программа покажет его пароль, если он есть в базе данных
_(данная функция служит для проверки слива вашего пароля в сеть)_

### Поиск по фото
Загружаете фото человека, которого хотите найти, выбирайте его пол для более быстрого поиска (если программа не нашла, можете попробовать сменить пол) после поиска вам покажут все найденные сходства человека, и выведет списком его имя, id "ВК" и ссылку на страничку. Поиск работает только на территории Красноярска

### Поиск по имени
На данный момент в разработке. Можно будет ввести как ФИО человека, так его псевдоним. В ответ программа выдаст номер телефона

### Доп. 
- Настройки
- Уведомления о завершении поиска информации
- Обратная связь с разработчиком 

## Технология работы
### Основные библиотеки
- PyQt5
- QThread
- Urllib
- json
- sqlite
- vk_api
- numpy
- dlib
- skimage

### Реализация - поиск по номеру
Пользователь вводит номер телефона. Программа проверяет его на правильный формат. Если всё правильно, то формируется запрос на API адрес. Если всё успешно, показываем найденную информацию, иначе возвращаем ошибку

### Реализация - поиск по email
Для работы с email были скачены разные базы слитых паролей. С помощью скрипта информация была переброшена в sqlite bd. _(sript path: pars_file/pars_email.py)_
Пользователь вводит email. Происходит проверка на валидность и после чего идёт поиск в бд

### Реализация - поиск по фото
Для формирования поиска по фото были сделаны следующие шаги:
- Парсинг пользователей вк
- Формирование бд с данными
- Поиск по схожих данных в бд

##### Парсинг
Производиться запрос на Vk API с определёнными параметрами (возраст, пол, город, день рождение). Дальше производим отбор нужных нам пользователей. Если акк открытый, открываем альбом и берём первые 20 фото при возможности. Начинаем каждое анализировать на наличия лица _(про анализ фото дальше)_ и записывать данные при положительном результате. Так перебираем до трёх положительных фото, после чего берём следующего пользователя. Если было найдено меньше 3 фото с лицом или 0, то оставляем данные пустыми. Если акк был закрытым, то проверяется аватарка
Для быстроты парсинга было сделано два скрипта для мужского и женского пола _(script path: pars_file/parser_vk_man.py or pars_file/parser_vk_woman.py)_

_Пометка: На данный момент в бд есть пользователи 16, 17, 18 лет города Крск_
_(Прошло полгода, и я уже точно не помню какой возраст парсил)_

##### Анализ фото
Получаем фотографию и первым делом определяем на ней лицо. Для этого используем модель _shape_predictor_68_face_landmarks.dat_ из библиотеки dlib. После чего на обработанном фрагменте ищем дескрипторы _модель dlib_face_recognition_resnet_model_v1.dat_. Это та самая информация, по который мы будем сравнивать людей. Она хранит в себе определённые значения точек лица. Если точки были найдены, то добавляем данного пользователя в бд, иначе пропускаем

##### Поиск по фото
При самом поиске берётся загруженная фотка, анализируется и после данные начинают сравниваться с имающимися в бд. Данное сравнение происходит с помощью высчитывания евклидового расстояния (если кратко, то это расстояние между точками в трёхмерном пространстве). Если данное расстояние "< 0.56", то сходство есть и найденный пользователь добавляется в итоговый список. Как проверка пройдёт, выводится список всех похожих пользователей в виде таблицы

_Пометка: дескрипторы достаточно не точные, и в итоге можно получить приличный список схожих людей_

## Установка
Устанавливаем нужные библиотеки
```
pip install -r requirements.txt
```
После чего можем работать с основной программой, запустив файл _main.py_

Для работы формы обратной связи нужно заполнить данные в файле _config.py_
##### MY_ID
- ваш айди в вк. Для этого переходим в настройки-общее. Жмём на адрес страницы и тут будет написан ваш ID _(или используйте другой удобный способ для вас)_
##### VK_GROUP 
- для этого нужно будет создать сообщество вконтакте. Можно сразу перевести его в группу, чтобы сделать закрытый тип
- После этого переходим в управление-работа с API и тут создаём ключ, выдавая ему определённые права _(лучше выдать все сразу)_. Это и есть наш VK_GROUP. Но для корректной работы нужно сделать ещё некоторые шаги.
- Находясь в разделе "Работа с API" переходим на "Long Poll API", где в настройках включаем Long Poll API и ставим последнюю версию. Тут же переходим в раздел "Типы событий" и выставляем нужные права для отправки сообщения. _(Также можно поставить все)_.
- Теперь остаётся последний шаг. Переходим на главную страницу сообщества, в панели справа нажимаем "Ещё-Разрешить сообщения"  

Для запуска парсинг файлов нужно в файле _config.py_ заполнить VK_TOKEN

##### VK_TOKEN
- Переходим по [ссылке](https://vk.com/apps?act=manage) для регистрации приложения вк
- Нажимаем создать
- Пишем любое название и выбираем "Standalone-приложение"
- Переходим в панель настройки и копируем ID приложения. После вставляем сюда в id -> https://oauth.vk.com/authorize?client_id=1234567&scope=215985366&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1
- Переходим по ссылке и даём доступ, после чего в адресной строке будет ссылка. Копируем наш токен после "access_token=". Это и есть наш токен
_(Это ваше приложение и данные никуда не утекут, главное не показывайте никому этот код)_

pip install PyQt5
pip install vk_api
pip install scikit-image
pip install opencv-python
pip install cmake