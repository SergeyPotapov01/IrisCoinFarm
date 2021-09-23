import time
import threading
import sqlite3

from random import randint

import vk_api

__version__ = '1.0.0'


class DataBase:
    def __init__(self):
        self.tokens = [0] # ноль лишь потому что если только один токен в массиве, то обработчик проходит по строке в цикле фор

    def _addToken(self, token: str):
        self.tokens.append(token)

    def createDB(self):
        try:
            with sqlite3.connect('access_token.db') as con:
                cur = con.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS access_tokens(
                    access_token MESSAGE_TEXT PRIMARY KEY 
                    )
                """)
        except:
            print('хуй знает что могло пойти не так при создании таблицы')

    def sendTokenToDB(self, token):
        try:
            with sqlite3.connect('access_token.db') as con:
                cur = con.cursor()
                cur.execute('INSERT INTO access_tokens(access_token) VALUES ("{0}")'.format(token))
                con.commit()
            self._addToken(token)
        except sqlite3.IntegrityError:
            print('Повторно введены данные к одному аккаунту')

    def loadDB(self):
        try:
            with sqlite3.connect('access_token.db') as con:
                cur = con.cursor()
                z = cur.execute('SELECT access_token FROM access_tokens')
                for token in z:
                    self.tokens.append(token)
        except sqlite3.OperationalError:
            print('База данных не создана, Сейчас ее создам')
            self.createDB()

    def getTokenAndSendToDB(self, login, password):
        vk_session = vk_api.VkApi(login, password, app_id=2685278)
        vk_session.auth()
        self.sendTokenToDB(vk_session.token['access_token'])

    def deleteInvalidToken(self, token):
        try:
            with sqlite3.connect('access_token.db') as con:
                cur = con.cursor()
                cur.execute('DELETE FROM access_tokens WHERE access_token="{0}"'.format(token))
                con.commit()
            self.tokens.remove(token)
        except:
            print('А хуй знает что могло пойти не так при удалении инвалид токена из бд')


def irisCoinFarm(*dataBase):
    while crutch:
        try:
            for access_token in dataBase:
                if access_token == 0:
                    continue # кароче ебать баг если только один токен в массиве, то он итерируется по токену, а не по массиву оставлю это как костыль

                vk = vk_api.VkApi(token=access_token)
                vk = vk.get_api()
                try:
                    vk.wall.createComment(owner_id=-174105461, post_id=6713149, message='Ферма')
                except vk_api.exceptions.ApiError:
                    dataBase.deleteInvalidToken(access_token)
                    print('Токен инвалид надо переделать')
                print('токен обработан')
                time.sleep(10)
            print('Все токены обработанны, ухожу на сон 4 часа')
            time.sleep(60*60*4 + randint(180, 420))
        except:
            print('Случилась какая то хуета я потом распишу эксепшены')
            time.sleep(1)


if __name__ == '__main__':
    crutch = True
    dataBase = DataBase()
    dataBase.loadDB()
    tread = threading.Thread(target=irisCoinFarm, args=dataBase.tokens)
    tread.start()
    while True:
        q = input('Введите цифру:\n 1 - Добавить аккаунт по паролю \n 2 - Закрыть программу ')
        if q == '1':
            login = input('Введи логин: ')
            password = input('Введи пароль')
            dataBase.getTokenAndSendToDB(login=login, password=password)
        elif q == '2':
            print('Закрытие программы')
            crutch = False
            break
        else:
            print('Ты ввел какую то хуйню, введи еще раз но без пробелов')