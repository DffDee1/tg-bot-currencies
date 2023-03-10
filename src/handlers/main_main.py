from aiogram import F, types

from src import config
from src.centralBank import CBFunctions
from src.keyboards import make_keyboard
from src.states import *
from src.bot import router, bot, db


@router.message(Main.main, F.text.casefold() == "основные")
async def process_main_default(message: types.Message) -> None:
    """
    Раздел "Основные валюты"
    """

    keyboard = await make_keyboard(['Обновить', 'Назад'])
    currencies = await CBFunctions.get_base_currencies()
    text = ''

    user_currency = await db.select_from_table('users', 'ex_currency', f'WHERE tg_id={message.chat.id}')
    user_currency = user_currency[0][0]

    for currency in currencies:
        try:
            flag = config.FLAGS[currency[0]['CharCode'][:2]]
        except KeyError:
            flag = "🏳️"
        price = await CBFunctions.get_course(currency[0], 1, user_currency)
        text += f'{flag}{price[1]} {" ".join(currency[0]["Name"].split()[:2])}: {round(price[0], 2)} {user_currency}\n'

    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)


@router.message(Main.main, F.text.casefold() == "обновить")
async def process_default_update(message: types.Message) -> None:
    """
    Раздел "Основные валюты" - Обновление котировок
    """
    await process_main_default(message)
