import time
import datetime
import threading
import sqlite3

from random import randint

import requests
import vk_api

__version__ = '1.1.0'


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
                    access_token TEXT,
                    id INTEGER PRIMARY KEY  NOT NULL,
                    )
                """)
        except:
            print('хуй знает что могло пойти не так при создании таблицы')

    def sendTokenToDB(self, token: str):
        try:
            vk = vk_api.VkApi(token=token)
            vk = vk.get_api()
            id = str(vk.users.get()[0]['id'])
            with sqlite3.connect('access_token.db') as con:
                cur = con.cursor()
                cur.execute(f'INSERT INTO access_tokens(access_token, id) VALUES ("{token}", {id})')
                con.commit()
            self._addToken(token)
        except sqlite3.IntegrityError:
            print('Повторно введены данные к одному аккаунту')
        except requests.exceptions.ConnectionError:
            print('Проблема с тынтырнетом')

    def loadDB(self):
        try:
            with sqlite3.connect('access_token.db') as con:
                cur = con.cursor()
                z = cur.execute('SELECT access_token FROM access_tokens')
                for token in z:
                    self.tokens.append(token[0])
        except sqlite3.OperationalError:
            print('База данных не создана, Сейчас ее создам')
            self.createDB()

    def getTokenAndSendToDB(self, login: str, password: str ):
        vk_session = vk_api.VkApi(login, password, app_id=2685278)
        vk_session.auth()
        self.sendTokenToDB(vk_session.token['access_token'])

    def deleteInvalidToken(self, token):
        try:
            with sqlite3.connect('access_token.db') as con:
                cur = con.cursor()
                cur.execute(f'DELETE FROM access_tokens WHERE access_token="{token}"')
                con.commit()
            self.tokens.remove(token)
        except:
            print('А хуй знает что могло пойти не так при удалении инвалид токена из бд')


def irisCoinFarm(*dataBase: str):
    time.sleep(5)
    while crutch:
        if True:
            for access_token in dataBase:
                if access_token == 0:
                    continue # кароче ебать баг если только один токен в массиве, то он итерируется по токену, а не по массиву оставлю это как костыль

                vk = vk_api.VkApi(token=access_token)
                vk = vk.get_api()

                try:
                    vk.wall.createComment(owner_id=-174105461, post_id=6713149, message='Ферма')
                    id = str(vk.users.get()[0]['id'])
                    print(f'Комментарий на фарм создан с id{id} в ' +str(datetime.datetime.today()))
                except vk_api.exceptions.ApiError:
                    dataBase.deleteInvalidToken(access_token)
                    print(f'Токен инвалид надо переделать{access_token}')
                except requests.exceptions.ConnectionError:
                    print('Проблема с тынтырнетом надо будет это переписать, а то как не кайф')
                time.sleep(10)
            print('Все токены обработанны, ухожу на сон 4 часа') # перепишу под асинхрон что бы каждый токен сам засыпал на 4 часа
            print(datetime.datetime.today())
            time.sleep(60*60*4 + randint(180, 420))

if __name__ == '__main__':
    crutch = True
    dataBase = DataBase()
    dataBase.loadDB()
    tread = threading.Thread(target=irisCoinFarm, args=dataBase.tokens)
    tread.start()
    while True:
        q = input('Введите цифру:\n 1 - Добавить аккаунт по паролю \n 2 - Добавить токен в БД(если токен инвалид, то его дропнет с бд)\n 3 - Закрыть программу \n')
        if q == '1':
            login = input('Введи логин: ')
            password = input('Введи пароль: ')
            try:
                dataBase.getTokenAndSendToDB(login=login, password=password)
            except vk_api.exceptions.BadPassword:
                print('Неверно введен логин либо пароль')
        elif q == '2':
            token = input('Введи токен: ')
            dataBase.sendTokenToDB(token)
        elif q == '3':
            print('Закрытие программы')
            crutch = False
            break
        else:
            print('Ты ввел какую то хуйню, введи еще раз но без пробелов')