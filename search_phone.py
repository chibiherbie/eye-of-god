import urllib.request  # для открытия ссылок
import json
import webbrowser


def phone_info_main(phone):
    getInfo = "https://htmlweb.ru/geo/api.php?json&telcod=" + phone  # формируем запрос

    try:
        infoPhone = urllib.request.urlopen(getInfo)  # открываем запрос
        infoPhone = json.load(infoPhone)

        # print("Номер телефона", "+" + phone)
        # print("Страна", infoPhone["country"]["name"])
        # print("Регион", infoPhone["region"]["name"])
        # print("Оператор", infoPhone["0"]["oper"])
        # print("Часть света", infoPhone["country"]["location"])
        return infoPhone["region"]["name"], infoPhone["0"]["oper"], infoPhone["country"]["name"]

    except Exception as e:
        print("Телефон не найден")
        return 'Телефон не найден', 'Телефон не найден', 'Телефон не найден'


def phone_info_db():
    pass


def phone_info_tg():
    pass


def phone_info_ads():
    pass


def phone_info_soc():
    pass