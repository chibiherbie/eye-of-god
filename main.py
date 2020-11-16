import sys

from PyQt5 import uic, QtCore, QtWidgets, QtMultimedia
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QStatusBar,\
    QTableWidgetItem, QMessageBox, QWidget, QLabel, QAction, QDesktopWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor

import webbrowser
import vk_api
from datetime import datetime

import search_phone
import search_photo
import search_email
import config

print('asd')


##########################
# Загрузка
##########################
class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 500)

        # загружаем лого
        self.label_anim = QLabel(self)
        self.pic = QPixmap('img/icon.png')
        self.label_anim.setPixmap(self.pic)

        # Удаляем стандартныйы бар
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # удаляет окно
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # делаем фон прозрачным

        # переменная выхода из цикла
        self.counter_exit_screen = 0

        # устанавливаем таймер
        self.timer = QTimer()
        self.timer.timeout.connect(self.loading_screen_progress)
        self.timer.start(15)  # запусккаем таймер в милисекундах

    def loading_screen_progress(self):
        if self.counter_exit_screen > 100:
            self.timer.stop()  # останавливаем таймер

            self.main = MainWindow()
            self.main.show()  # запускаем главное окно

            self.close()  # закрываем окно загрузки

        self.counter_exit_screen += 1


##########################
# Главный экран
##########################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/main.ui', self)  # Загружаем дизайн

        # кнопки для открытия других форм
        self.btn_number.clicked.connect(self.open_form_number)
        self.btn_email.clicked.connect(self.open_form_email)
        self.btn_name.clicked.connect(self.open_form_name)
        self.btn_photo.clicked.connect(self.open_form_photo)

        # временный запрет
        self.btn_name.setEnabled(False)
        # временный запрет

        # self.loading_screen = LoadingScreen

        self.initUI()

    # доп интерфейс - меню бар
    def initUI(self):
        # созздаём меню бар
        self.menuBar = self.menuBar()
        self.menuBar.setStyleSheet('QMenuBar {color: white;} QMenuBar::item:selected {color: black}')

        # добовляем эелемент в меню бар
        app = self.menuBar.addMenu('Приложение')
        app.setStyleSheet('QMenu::item{color: white} QMenu::item:selected {background-color: rgb(85, 85, 85);}')

        # создаём действия для элемента
        settings_action = QAction('Настройки', self)
        settings_action.triggered.connect(self.open_settings)
        settings_action.setShortcut('Ctrl+K')  # hotkey

        feedback_action = QAction('Обратная связь', self)
        feedback_action.triggered.connect(self.open_feedback)

        app.addActions([settings_action, feedback_action])  # добовляем дейсвтия в эелемент

    # открытие окна для поиска по номеру
    def open_form_number(self):
        self.form_number = NumberForm()
        self.form_number.show()

    # открытия окна для поиска по email
    def open_form_email(self):
        self.form_email = EmailForm()
        self.form_email.show()

    # открытия окна для поиска по имени
    def open_form_name(self):
        self.form_name = NameForm()
        self.form_name.show()

    # открытия окна для поиска по фото
    def open_form_photo(self):
        self.form_photo = PhotoForm()
        self.form_photo.show()

    # октрытия окна настроек
    def open_settings(self):
        self.form_settings = SettingsForm()
        self.form_settings.show()

    # открытие окна обратной связи
    def open_feedback(self):
        self.form_feedback = FeedbackForm()
        self.form_feedback.show()

    # обработка закрытия окна
    def closeEvent(self, event):
        sys.exit()  # завершаем работу всей программы


##########################
# уведомление
##########################
class Notification(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/Notification.ui', self)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        resolution = QDesktopWidget().screenGeometry(-1)

        self.count_messages = 0

        # self.mainLayout = QVBoxLayout(self)

        # распологаем ууведомленеи в левом веррхнем углу
        self.move(resolution.width() - 315, resolution.height() - 90 * resolution.height() / 100)

        # делаем тамер
        self.timer = QTimer()
        self.timer.timeout.connect(self.time_notice)

        # переменная выхода из цикла
        self.counter_exit = 0

    # закрываем уведомление
    def close_notification(self):
        # self.mainLayout.removeWidget(self.sender().parent())
        # self.sender().parent().deleteLater()
        self.count_messages -= 1
        self.adjustSize()
        if self.count_messages == 0:
            self.close()

    # поазываем уведомление
    def show_notice(self, message):
        self.msg.setText(str(message))
        # self.mainLayout.addWidget(self.)
        self.btn_close.clicked.connect(self.close_notification)
        self.count_messages += 1

        # Таймер в милисекундах
        self.timer.start(35)

        self.show()

    # таймер
    def time_notice(self):
        if self.counter_exit > 100:
            self.timer.stop()  # останавливаем таймер
            self.close()  # закрываем окно

        self.counter_exit += 1


##########################
# общии свойста для остальных окон
##########################
class CommonProperties(QMainWindow):
    def __init__(self):
        super().__init__()

        # заружаем настройки
        with open('logs/settings.txt') as f:
            settings = [int(i) for i in f.read().split(';')]

        # запоминаем настройки
        self.volume = settings[0]
        self.push_notification = any([settings[1]])
        self.sound_notification = any([settings[2]])

        # загрузка звукового уведомления
        media = QtCore.QUrl.fromLocalFile('D:/test/sound/alert.mp3')
        content = QtMultimedia.QMediaContent(media)
        self.player_alert = QtMultimedia.QMediaPlayer()
        self.player_alert.setMedia(content)

        # стиль кнопки
        self.btn_design = 'QPushButton {background-color: {COLOR};color:' \
                                      ' black;border-radius: 9px;height: 22px;} QPushButton:hover' \
                                      ' {background-color: rgb(208, 208, 208);color: rgb(45, 45, 45);}' \
                                      'QPushButton:pressed {background-color: rgb(207, 207, 207);}'

    # обработка нажатий
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:  # обработка с помощью кнопки 'enter'
            print('enter')
            if self.__class__.__name__ == 'NumberForm':
                self.check_number()
            elif self.__class__.__name__ == 'EmailForm':
                self.search_email()
            elif self.__class__.__name__ == 'NameForm':
                pass
            elif self.__class__.__name__ == 'PhotoForm':
                self.search_photo()
            elif self.__class__.__name__ == 'FeedbackForm':
                self.send_msg()

        elif event.key() == Qt.Key_Escape:  # выход из формы
            print('escape')
            self.close()

    # запуск уведомления
    def start_notification(self, msg):
        if self.push_notification:
            self.notification = Notification()
            self.notification.show_notice(msg)

    # завершение поиска
    def end_search(self, text='Поиск закончен: 100%'):
        # проигрываем уведомление
        if self.sound_notification:
            self.player_alert.setVolume(self.volume)
            self.player_alert.play()

        # Включаем кнопку
        if self.__class__.__name__ == 'PhotoForm':
            self.btn_search_photo.setEnabled(True)
            self.btn_search_photo.setStyleSheet(self.btn_design.replace('{COLOR}', 'rgb(255, 255, 255)'))
        elif self.__class__.__name__ == 'NumberForm':
            self.btn_search_number.setEnabled(True)
            self.btn_search_number.setStyleSheet(self.btn_design.replace('{COLOR}', 'rgb(255, 255, 255)'))
        elif self.__class__.__name__ == 'EmailForm':
            self.btn_search_email.setEnabled(True)
            self.btn_search_email.setStyleSheet(self.btn_design.replace('{COLOR}', 'rgb(255, 255, 255)'))


##########################
# настройки
##########################
class SettingsForm(CommonProperties):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/settings.ui', self)

        # записываем предыдущие настройки
        if not self.push_notification:
            self.btn_enabled_push.setChecked(False)

        if not self.sound_notification:
            self.btn_enabled_sound.setChecked(False)

        self.edit_slider_sound.setValue(self.volume)
        self.edit_spin_sound.setValue(self.volume)

        # подключаемся к обработчику
        self.btn_enabled_push.clicked.connect(self.change_settings)
        self.btn_enabled_sound.clicked.connect(self.change_settings)
        self.edit_spin_sound.valueChanged.connect(self.change_settings)
        self.edit_slider_sound.valueChanged.connect(self.change_settings)

    # соранение настоящих настроек в файл
    def save_settings(self):
        with open('logs/settings.txt', mode='w', encoding='utf8') as f:
            p = 1 if self.push_notification else 0
            t = 1 if self.sound_notification else 0
            f.write(f'{self.volume};{p};{t}')

    def closeEvent(self, event):
        self.save_settings()

    # записываем изменения настроек
    def change_settings(self):
        self.push_notification = 1 if self.btn_enabled_push.isChecked() else 0  # пуш уведомление
        self.sound_notification = 1 if self.btn_enabled_sound.isChecked() else 0  # звук ууведомление

        if self.volume != self.edit_spin_sound.value():
            self.volume = self.edit_spin_sound.value()
            self.edit_slider_sound.setValue(self.volume)

        self.volume = self.edit_slider_sound.value()  # звук
        self.edit_spin_sound.setValue(self.volume)

        # сохраняем настройки
        self.save_settings()


##########################
# обраятная связь
##########################
class FeedbackForm(CommonProperties):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/feedback.ui', self)

        # подлючаем кнопку
        self.btn_send_msg.clicked.connect(self.send_msg)

        self.initUI()

    # отправляем сообщение
    def send_msg(self):

        # если есть данные
        if self.edit_name.text() and self.edit_msg.toPlainText():
            self.statusBar.showMessage('')  # чистим статус бар

            # подключаемся к вк
            vk_session = vk_api.VkApi(token=config.VK_TOKEN)
            vk = vk_session.get_api()

            # собираем сообщение
            m = f'Имя:{self.edit_name.text()}\n\nДата-время: {datetime.now()}\n\n сообщение\n' \
                f'--------------------\n{self.edit_msg.toPlainText()}\n--------------------'

            vk.messages.send(chat_id='215', message=m, random_id=0)  # оправляем сообщение

            self.close()  # закрываем окно

            QMessageBox.about(self, 'Информация', 'Сообщение отправлено')  # говорим о успешной отправки сообщения
            # msg_box.setWindowTitle('Информация')
            # msg_box.setText('Сообщение отправлено')
            # msg_box.setIcon(QMessageBox.Information)
            # msg_box.addButton('Окей', QMessageBox.AcceptRole)
            # msg_box.exec()
        else:
            self.statusBar.showMessage('Не заполнены данные')

    # подключаем статус бар для отображения данных
    def initUI(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet("background-color: rgb(45, 45, 45); color: red")


##########################
# поиск номера телефона
##########################
class NumberForm(CommonProperties):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/number.ui', self)

        # подключаем кнопки
        self.btn_search_number.clicked.connect(self.check_number)
        self.btn_whatsapp.clicked.connect(self.phone_btn_soc)
        self.btn_viber.clicked.connect(self.phone_btn_soc)

        self.progressbar_number = ProgressBarThread(NumberForm=self)  # подключаемся к QThread

        self.true_number = ''  # запоменания настоящего номера

        self.initUI()

    # подключаем статус бар для отображения данных
    def initUI(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet("background-color: rgb(45, 45, 45); color: red")

        # обнуляем текст
        self.region_text.setText('')
        self.operator_text.setText('')
        self.country_text.setText('')

    # открытие ссылки для номера
    def phone_btn_soc(self):
        if self.true_number:
            if self.sender().text() == 'WhatsApp':
                webbrowser.open('https://api.whatsapp.com/send?phone=' + self.true_number, new=2)
            elif self.sender().text() == 'Viber':
                webbrowser.open('viber://add?number=+' + self.true_number, new=2)

    # проверка номера на валидность и отправление на поиск
    def check_number(self):
        number = list(self.edit_number.text())  # загружаем введёный номер

        self.true_number = ''

        is_double = False  # для проверки двойных скобок

        class Error(Exception):
            pass

        # проверка номера на валидность
        try:
            if not number:
                raise Error('Пустое значение')

            for i in range(len(number)):
                if number[0] == '-' or number[-1] == '-':
                    raise Error('Неверынй формат')

                # если быыло две открытых скобки подряд
                if number[i] == '(' and not is_double:
                    is_double = True
                elif number[i] == '(' and is_double:
                    raise Error('Неверынй формат')

                # ксли было две зкартыых скобки подряд
                if number[i] == ')' and is_double:
                    is_double = False
                elif number[i] == ')' and not is_double:
                    raise Error('Неверынй формат')

                if number[i] in '0123456789':
                    self.true_number += number[i]

                if number[i] == '-':
                    if i < len(number):
                        if number[i + 1] == '-':
                            raise Error('Неверынй формат')

                if str(number[i]).lower() in 'qwertyuiopasdfghjklzxcvbnm':
                    raise Error('Неверный формат')

            if len(self.true_number) == 11 and not is_double:
                if self.true_number[0] == '8':
                    self.true_number = self.true_number.replace('8', '7')

                # print(self.true_number)
                self.statusBar.setStyleSheet("color: white")

                # подключаем поток для параллельной обработки
                self.progressbar_number.progress.connect(self.change_number, QtCore.Qt.QueuedConnection)
                self.progressbar_number.show_notification.connect(self.start_notification, QtCore.Qt.QueuedConnection)
                self.progressbar_number.start()  # запускаем

                # отключаем кнопку
                self.btn_search_number.setEnabled(False)
                self.btn_search_number.setStyleSheet(self.btn_design.replace('{COLOR}', 'rgb(120, 120, 120)'))
            else:
                raise Error('Неверное количество цифр')

        # если неверный номер
        except Error as er:
            print(er)
            self.statusBar.showMessage(str(er))
            self.statusBar.setStyleSheet("color: red")

    # отображение прогресса
    def change_number(self, s):
        self.statusBar.showMessage(f'Начинаем поиск: {str(int(s))}%')
        if s >= 100:
            self.statusBar.showMessage(f'Поиск закончен: 100%')

    # закрытие приложения
    def closeEvent(self, event):
        # диалог для заккртия
        reply = QMessageBox.question(self, 'Информация', "Вы уверены, что хотите закрыть окно?",
                                        QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # зарываем поток
            self.progressbar_number.terminate()

            # закрываем форму
            super(NumberForm, self).closeEvent(event)
        else:
            event.ignore()


##########################
# поиск email
##########################
class EmailForm(CommonProperties):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/email.ui', self)

        # подключаем кнопку
        self.btn_search_email.clicked.connect(self.search_email)

        # обнуляем текст
        self.email_text.setText('')
        self.pass_text.setText('')

        self.multitasking_email = ProgressBarThread(EmailForm=self)  # подключаемся к QThread

        self.initUI()

    # подклкючаем интерфейс (статус бар)
    def initUI(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet("background-color: rgb(45, 45, 45); color: white;")

    # поиск почты
    def search_email(self):
        self.email = self.edit_email.text()  # берём почту

        if self.email.count('@') == 1:
            # подключаем поток для параллельной обработки
            self.multitasking_email.progress.connect(self.change_progress, QtCore.Qt.QueuedConnection)
            self.multitasking_email.show_notification.connect(self.start_notification, QtCore.Qt.QueuedConnection)
            self.multitasking_email.start()  # запускаем поток

            self.statusBar.showMessage('Начинаем поиск: 0%')

            # выключаем кнопку
            self.btn_search_email.setEnabled(False)
            self.btn_search_email.setStyleSheet(self.btn_design.replace('{COLOR}', 'rgb(120, 120, 120)'))
        else:
            self.statusBar.showMessage('Неверный формат')

    # отображение прогресса
    def change_progress(self, s):
        self.statusBar.showMessage(f'Начинаем поиск: {str(int(s))}%')
        if s >= 100:
            self.statusBar.showMessage(f'Поиск закончен: 100%')

    # закрытие приложения
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Информация', "Вы уверены, что хотите закрыть окно?",
                                        QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # зарываем поток
            self.multitasking_email.terminate()

            # закрываем форму
            super(EmailForm, self).closeEvent(event)
        else:
            event.ignore()


##########################
# поиск имени
##########################
class NameForm(CommonProperties):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/name.ui', self)


##########################
# поиск фото
##########################
class PhotoForm(CommonProperties):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/photo.ui', self)

        # стиль дял подсказки, которая высвечивается при наведении
        self.setStyleSheet("""QToolTip { 
                                   background-color: black; 
                                   border: 1px solid white;
                                   border-radius: 4px;
                                   }""")

        # подключаем кнопки
        self.btn_upload.clicked.connect(self.upload)
        self.btn_search_photo.clicked.connect(self.search_photo)
        self.btn_sort.clicked.connect(self.sort_name)
        self.btn_open_url.clicked.connect(self.open_url)

        # добовляем текст в подсказку
        self.label_add.setToolTip('Включает в себя дополнительную проверку фото\nУвеличивается время обработки.'
                                  '\nТакже присутствует возможность потерять человека которого Вы ищете ')

        # распределяем столбцы по ширине таблицы
        header = self.table_result.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.progressbar_photo = ProgressBarThread(PhotoForm=self)

        self.os_name = ''
        self.users_table = []

        self.initUI()

    # подключаем статус бар для отображения данных
    def initUI(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet("background-color: rgb(45, 45, 45); color: white;")

        # загрузочная картина - лого
        self.pixmap = QPixmap('img/icon.png')
        self.pixmap_icon = self.pixmap.scaled(211, 211)
        self.pic.setPixmap(self.pixmap_icon)

    # загрузка и отоброжение фото
    def upload(self):
        try:
            # поулчаем путь до фото
            self.os_name = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg *.png)')[0]

            if self.os_name:  # если фото было выбрано
                # устанавливаем фотоку и меняем размер
                self.pixmap = QPixmap(self.os_name)
                self.pixmap1 = self.pixmap.scaled(211, 211, QtCore.Qt.KeepAspectRatio)
                self.pic.setPixmap(self.pixmap1)

                self.statusBar.showMessage('Фотка загружена')
            else:
                # если фотки не было
                self.statusBar.showMessage('Фотка не загружена')
                self.pic.setPixmap(self.pixmap_icon)
        except Exception:
            self.statusBar.showMessage('Ошибка')

    # получаем данные и запускаем поиск
    def search_photo(self):
        self.gender = 1  # 1 - девушки, 2 - парни
        self.add_search = False  # доп поиск

        if self.os_name:
            self.statusBar.showMessage('Начинаем поиск: 0%')

            if self.btn_man.isChecked():  # проверка на пол
                self.gender = 2

            if self.btn_add_search.isChecked():  # проверка на доп проверку
                self.add_search = True

            # подключаем поток для параллельной обработки
            self.progressbar_photo.progress.connect(self.change, QtCore.Qt.QueuedConnection)
            self.progressbar_photo.show_notification.connect(self.start_notification, QtCore.Qt.QueuedConnection)
            self.progressbar_photo.start()  # запусаем поток

            # Выключаем кнопку
            self.btn_search_photo.setEnabled(False)
            self.btn_search_photo.setStyleSheet(self.btn_design.replace('{COLOR}', 'rgb(120, 120, 120)'))
        else:
            self.statusBar.showMessage('Фотка не загружена')

    # отображение прогресса
    def change(self, s):
        self.statusBar.showMessage(f'Начинаем поиск: {str(int(s))}%')
        if s >= 100:
            self.statusBar.showMessage(f'Поиск закончен: 100%')

    # закрытие приложения
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Информация', "Вы уверены, что хотите закрыть окно?",
                                        QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # зарываем поток
            self.progressbar_photo.terminate()

            # закрываем форму
            super(PhotoForm, self).closeEvent(event)
        else:
            event.ignore()

    # сортируем таблицу по имени
    def sort_name(self):
        self.users_table.sort(key=lambda x: str(self.edit_name_sort.text()).lower() in x[1].lower(),
                              reverse=True)

        if self.users_table:
            self.table_result.clearContents()

            # удаляем строки
            for row in range(len(self.users_table)):
                self.table_result.removeRow(row)

            # устанавливаем новые значения
            for i, row in enumerate(self.users_table):
                self.table_result.setRowCount(self.table_result.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.table_result.setItem(i, j, QTableWidgetItem(str(elem)))
                    self.table_result.item(i, j).setForeground(QColor(255, 255, 255))
        else:
            self.statusBar.showMessage('Нет данных в таблице')

    # открытие ссылок
    def open_url(self):
        if self.users_table:
            for i in range(self.edit_spin_first.value() - 1, self.edit_spin_second.value()):
                if len(self.users_table) > i >= 0:
                    webbrowser.open(self.users_table[i][2], new=2)
        else:
            self.statusBar.showMessage('Нет данных в таблице')


##########################
# ансинхронный класс
##########################
class ProgressBarThread(QThread):

    # сигналы
    progress = pyqtSignal(float)
    show_notification = pyqtSignal(str)

    def __init__(self, PhotoForm=None, NameForm=None, EmailForm=None, NumberForm=None):
        super().__init__()
        self.PhotoForm = PhotoForm
        self.NameForm = NameForm
        self.EmailForm = EmailForm
        self.NumberForm = NumberForm
        # self._init = False
        # self.downloaded = 0

    # определяем откуда сигнал
    def run(self):
        if self.NameForm:
            print('coming soon')

        elif self.PhotoForm:
            self.qthread_photo()

        elif self.EmailForm:
            self.qthred_email()

        elif self.NumberForm:
            self.qthread_number(self.NumberForm.true_number)

    # поиск фото
    def qthread_photo(self):
        # ищем сходства
        list_user = search_photo.search_photo_db(self.PhotoForm.os_name, self.PhotoForm.gender,
                                                 self.PhotoForm.add_search, ProgressBarThread=self)

        # если list_user список, то смотрим, иначе выводим в качестве ошибки
        if type(list_user) == list:

            self.PhotoForm.table_result.clearContents()

            # удаляем строки
            for row in range(len(self.PhotoForm.users_table)):
                self.PhotoForm.table_result.removeRow(row)

            # заполянем таблицу
            for i, row in enumerate(list_user):
                self.PhotoForm.table_result.setRowCount(self.PhotoForm.table_result.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.PhotoForm.table_result.setItem(i, j, QTableWidgetItem(str(elem)))
                    self.PhotoForm.table_result.item(i, j).setForeground(QColor(255, 255, 255))

            # завершаем поиск. выводим пуш и звук уведомление
            self.PhotoForm.end_search()
            self.show_notification.emit('Поиск фото завершён')

            self.PhotoForm.users_table = list_user[:]  # запоминаем данныые для сортировки
        else:
            self.PhotoForm.end_search(list_user)

            self.show_notification.emit('Произошла ошибка')

    # поиск номера
    def qthread_number(self, phone):
        number_info = search_phone.phone_info_main(phone)  # получаем поисковые данные

        # выводим данные
        self.NumberForm.region_text.setText(number_info[0])
        self.NumberForm.operator_text.setText(number_info[1])
        self.NumberForm.country_text.setText(number_info[2])

        # завершаем поиск. выводим пуш и звук уведомление
        self.NumberForm.end_search()
        self.show_notification.emit('Поиск номера завершён')

    # поиск почты
    def qthred_email(self):
        # ищем почту в бд
        data = search_email.search_email_db(self.EmailForm.email, ProgressBarThread=self)

        if data:  # если получили результат
            self.EmailForm.email_text.setText(str(data[1]))
            self.EmailForm.pass_text.setText(str(data[2]))
        else:
            self.EmailForm.email_text.setText(self.EmailForm.email)
            self.EmailForm.pass_text.setText('Не найдено')

        # завершаем поиск. выводим пуш и звук уведомление
        self.EmailForm.end_search()
        self.show_notification.emit('Поиск почты завершён')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LoadingScreen()
    ex.show()  # показываем загруочный экран
    sys.exit(app.exec_())