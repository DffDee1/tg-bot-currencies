# Включаем логирование
import asyncio
import logging

from aiogram import Bot, Dispatcher, Router

from src import config
from src.database import Postgres

logging.basicConfig(level=logging.INFO)


# Объекты бота и диспетчера (корневой роутер)
# Токен бота берется из файла config.py
bot = Bot(token=config.TOKEN, parse_mode="HTML")
dp = Dispatcher()

# роутер может маршрутизировать обновления, в него вложены сообщения и другие типы событий.
router = Router()

# Объект кастомного класса для базы данных postgress
db = Postgres()


async def main():
    from handlers import router

    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
