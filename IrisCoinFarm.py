import asyncio

from random import randint

from DataBase import DataBase

import requests
import vk_api

from loguru import logger


__version__ = '1.1.3'

logger.add('log/irisCoinFarm.log', format='{time} {level} {message}',
           level='INFO', rotation='1 week', compression='zip')

dataBase = DataBase()
FOREVER_LOOP = True


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
        except vk_api.exceptions.Captcha:
            logger.error('Капча, спим')
            await asyncio.sleep(randint(120, 600))
            continue
        await asyncio.sleep(60*60*4 + randint(120, 420))


async def asyncIrisCoinFarm(dataBase: DataBase):
    for access_token in dataBase.tokens:
        if access_token == 0:
            continue
        asyncio.ensure_future(_asyncIrisCoinFarm(access_token))

async def asyncUX(loop):
    while True:
        enteredQuery = await loop.run_in_executor(None, input, 'Введите цифру:\n 1 - Добавить аккаунт по паролю (отключили данную функцию) \n 2 - Добавить токен в БД(если токен инвалид, то его дропнет с бд)\n 3 - Показать аккаунты загруженные в бд \n 4 - Перезагрузить бота \n 5 - Закрыть программу \n')

        if enteredQuery == '1':
            continue
            login = input('Введи логин: ')
            password = input('Введи пароль: ')
            access_token = dataBase.getTokenAndSendToDB(login=login, password=password)
            if access_token == None:
                continue
            asyncio.ensure_future(_asyncIrisCoinFarm(access_token))

        elif enteredQuery == '2':
            token = input('Введи токен: ')
            access_token = dataBase.sendTokenToDB(token)
            if access_token == None:
                continue
            asyncio.ensure_future(_asyncIrisCoinFarm(access_token))
        elif enteredQuery == '3':
            for token in dataBase.sendID():
                logger.info('в БД присутствует id'+str(token[0]))

        elif enteredQuery == '4':
            logger.info('Перезагрузка бота')
            loop.stop()
            break

        elif enteredQuery == '5':
            logger.info('Закрытие программы')
            global FOREVER_LOOP
            FOREVER_LOOP = False
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
    while FOREVER_LOOP:
        try:
            logger.info('Event Loop запущен')
            asyncio.run(main())
        except RuntimeError:
            logger.info('Event Loop остановлен')
        except vk_api.exceptions.Captcha:
            logger.error('Капча В евент луп попала, хз почему')
