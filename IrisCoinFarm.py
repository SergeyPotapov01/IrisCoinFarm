import asyncio
import datetime

from random import randint

from DataBase import DataBase

import requests
import vk_api


__version__ = '1.1.1'

dataBase = DataBase()

async def _asyncIrisCoinFarm(access_token):
    while True:
        vk = vk_api.VkApi(token=access_token)
        vk = vk.get_api()
        try:
            vk.wall.createComment(owner_id=-174105461, post_id=6713149, message='Ферма')
            id = str(vk.users.get()[0]['id'])
            print(f'Комментарий на фарм создан с id{id} в ' + str(datetime.datetime.today()))
        except vk_api.exceptions.ApiError:
            dataBase.deleteInvalidToken(access_token)
            print(f'Токен инвалид надо переделать{access_token}')
        except requests.exceptions.ConnectionError:
            print('Проблема с тынтырнетом надо будет это переписать, а то как не кайф')
            await asyncio.sleep(10)
            continue
        await asyncio.sleep(60*60*4 + randint(180, 420))


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
                print('Неверно введен логин либо пароль')
        elif enteredQuery == '2':
            token = input('Введи токен: ')
            dataBase.sendTokenToDB(token)
        elif enteredQuery == '3':
            for token in dataBase.sendID():
                print(token[0])
        elif enteredQuery == '4':
            print('Закрытие программы')
            loop.stop()
            break
        else:
            print('Ты ввел какую то хуйню, введи еще раз но без пробелов')

async def main():
    loop = asyncio.get_event_loop()
    await asyncio.gather(
        asyncIrisCoinFarm(dataBase),
        asyncUX(loop),
    )

try:
    asyncio.run(main())
except RuntimeError:
    print('Event Loop остановлен')
