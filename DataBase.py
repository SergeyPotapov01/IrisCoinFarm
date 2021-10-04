import sqlite3
import vk_api

import requests


class DataBase:
    def __init__(self):
        self.tokens = [0] # ноль лишь потому что если только один токен в массиве, то обработчик проходит по строке в цикле фор
        self.loadDB()

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

    def sendID(self):
        try:
            with sqlite3.connect('access_token.db') as con:
                cur = con.cursor()
                z = cur.execute('SELECT id FROM access_tokens')
                return z
        except sqlite3.OperationalError:
            print('База данных не создана, Сейчас ее создам')
            self.createDB()

