import asyncio

from random import randint

from DataBase import DataBase

import requests
import vk_api

from  loguru import logger


__version__ = '1.1.2'

logger.add('log/irisCoinFarm.log', format='{time} {level} {message}',
           level='INFO', rotation='1 week', compression='zip')

dataBase = DataBase()


async def _asyncIrisCoinFarm(access_token):
    while True:
        vk = vk_api.VkApi(token=access_token)
        vk = vk.get_api()
        try:
            vk.wall.createComment(owner_id=-174105461, post_id=6713149, message='Ферма')
            id = str(vk.users.get()[0]['id'])
            logger.info(f'Комментарий на фарм создан с id{id}')
        except vk_api.exceptions.ApiError:
            dataBase.deleteInvalidToken(access_token)
            logger.error(f'Токен не действительный {access_token}')
        except requests.exceptions.ConnectionError:
            logger.error('Проблема с подключением к сети Интеррнет')
            await asyncio.sleep(30)
            continue
        await asyncio.sleep(60*60*4 + randint(120, 420))


async def asyncIrisCoinFarm(dataBase: DataBase):
    for access_token in dataBase.tokens:
        if access_token == 0:
            continue
        asyncio.ensure_future(_asyncIrisCoinFarm(access_token))

async def asyncUX(loop):
    while True:
        enteredQuery = await loop.run_in_executor(None, input, 'Введите цифру:\n 1 - Добавить аккаунт по паролю \n 2 - Добавить токен в БД(если токен инвалид, то его дропнет с бд)\n 3 - Показать аккаунты загруженные в бд \n 4 - Закрыть программу \n')

        if enteredQuery == '1':
            login = input('Введи логин: ')
            password = input('Введи пароль: ')

            try:
                dataBase.getTokenAndSendToDB(login=login, password=password)
            except vk_api.exceptions.BadPassword:
                logger.error('Неверно введен логин либо пароль')
            except vk_api.exceptions.LoginRequired:
                logger.error('Введена пустая строка логина')
            except requests.exceptions.ConnectionError:
                logger.error('Отсутствует логин')
            except vk_api.exceptions.PasswordRequired:
                logger.error('Отсутствует пароль')
                
        elif enteredQuery == '2':
            token = input('Введи токен: ')
            dataBase.sendTokenToDB(token)
        elif enteredQuery == '3':
            for token in dataBase.sendID():
                logger.info('в БД присутствует id'+str(token[0]))
        elif enteredQuery == '4':
            logger.info('Закрытие программы')
            loop.stop()
            break
        else:
            logger.error(f'%{enteredQuery}% - Не корректный запрос, попробуй еще раз')

async def main():
    loop = asyncio.get_event_loop()
    await asyncio.gather(
        asyncUX(loop),
        asyncIrisCoinFarm(dataBase),
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except RuntimeError:
        logger.info('Event Loop остановлен')
