import sqlite3


def search_email_db(email, ProgressBarThread):
    # подключаемся к бд
    con = sqlite3.connect('data/email/email.db')
    cur = con.cursor()

    count, progress = 0, 0.5  # переменная для постепенного взятия данных из бд и переменная для подсчета прогресса
    for i in range(100000, 1200001, 100000):
        email_pas = cur.execute('''SELECT * FROM emails WHERE id BETWEEN ? and ?''', (count, i)).fetchall()

        for em in email_pas:
            if email == em[1]:  # ищем сходства
                con.close()
                return em

        count += 100000
        progress += 100000 * 100 / 1200000
        ProgressBarThread.progress.emit(progress)  # отправялем сигнал для обновление статус бара

    con.close()


# print(search_email_db('jesus0z@gmail.com'))