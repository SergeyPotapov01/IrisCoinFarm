import sqlite3
import vk_api

import requests

from loguru import logger


logger.add('log/irisCoinFarm.log', format='{time} {level} {message}',
           level='INFO', rotation='1 week', compression='zip')

class DataBase:
    """
    Доступ к Базе данных осуществляется при при помощи данного экземпляра данного класса
    Позже надо провести рефакторинг и создание документации, возможно тут где то баги есть
    """
    def __init__(self):
        self.tokens = [0] # ноль лишь потому что если только один токен в массиве, то обработчик проходит по строке в цикле фор
        self.loadDB()

    def _addToken(self, token: str):
        self.tokens.append(token)

    def createDB(self):
        with sqlite3.connect('access_token.db') as con:
            cur = con.cursor()
            cur.execute("""
                CREATE TABLE access_tokens(
                access_token TEXT,
                id INTEGER PRIMARY KEY
                )
            """)

    def loadDB(self):
        try:
            with sqlite3.connect('access_token.db') as con:
                cur = con.cursor()
                z = cur.execute('SELECT access_token FROM access_tokens')
                for token in z:
                    self.tokens.append(token[0])
        except sqlite3.OperationalError:
            logger.error('База данных не создана, Сейчас ее создам')
            self.createDB()

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
            return token
        except sqlite3.IntegrityError:
            logger.error('Повторно введены данные к одному аккаунту')
        except requests.exceptions.ConnectionError:
            logger.error('Проблема с доступом к сети интернет')
        except vk_api.exceptions.ApiError:
            logger.error(f'Не действительный токен %{token}%')
        except vk_api.exceptions.Captcha:
            logger.error('Капча в БД')

    def getTokenAndSendToDB(self, login: str, password: str ):
        try:
            vk_session = vk_api.VkApi(login, password, app_id=2685278)
            vk_session.auth()
            self.sendTokenToDB(vk_session.token['access_token'])
            return vk_session.token['access_token']
        except vk_api.exceptions.BadPassword:
            logger.error('Неверно введен логин либо пароль')
        except vk_api.exceptions.LoginRequired:
            logger.error('Введена пустая строка логина')
        except requests.exceptions.ConnectionError:
            logger.error('Отсутствует логин')
        except vk_api.exceptions.PasswordRequired:
            logger.error('Отсутствует пароль')
        except vk_api.exceptions.Captcha:
            logger.error('Капча в БД')

    def deleteInvalidToken(self, token):
        try:
            with sqlite3.connect('access_token.db') as con:
                cur = con.cursor()
                cur.execute(f'DELETE FROM access_tokens WHERE access_token="{token}"')
                con.commit()
            self.tokens.remove(token)
        except:
            logger.error('А хуй знает что могло пойти не так при удалении инвалид токена из бд')

    def sendID(self):
        try:
            with sqlite3.connect('access_token.db') as con:
                cur = con.cursor()
                return cur.execute('SELECT id FROM access_tokens')
        except sqlite3.OperationalError:
            logger.error('Отсутствует база данных, создана новая')
            self.createDB()
