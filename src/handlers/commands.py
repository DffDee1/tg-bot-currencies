import re

from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from src import config
from src.centralBank import CBFunctions
from src.keyboards import make_default_keyboard
from src.states import *
from src.bot import router, bot, db


@router.message(F.text.casefold() == "назад")
async def process_case_add(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Main.main)
    await start_process(message, state)


@router.message(Command(commands=["info"]))
@router.message(F.text.casefold() == "info")
async def process_info(message: types.Message) -> None:
    text = config.USER_INSTRUCTION
    await bot.send_message(message.chat.id,
                           text)


@router.message(Command(commands=["all_currencies"]))
@router.message(F.text.casefold() == "all_currencies")
async def process_convert_choose_first_all_currencies(message: types.Message) -> None:
    """
    В чат отправляется полный список существующих валют
    """

    vals = await CBFunctions.get_all_currencies()
    text = "Список всех валют:\n\n"
    for val in vals:
        text += f"<b>{val['CharCode']}</b>: {val['Name']}\n"
    await bot.send_message(message.chat.id,
                           text)


# Хендлер для команды "/start"
@router.message(Command(commands=["start"]))
async def start_process(message: types.Message, state: FSMContext) -> None:
    """
    Раздел Старт
    """

    users_id = await db.select_from_table('users', params='tg_id')
    if str(message.chat.id) not in re.findall(r'\d+', str(users_id)[1:]):
        await db.insert_into_table('users',
                                'tg_id, ex_currency, fav_currency',
                                   [f"{message.chat.id}, 'RUB', 'USD'"])

    keyboard = await make_default_keyboard()

    try:
        user_currencies = await db.select_from_table('users', 'fav_currency, ex_currency',
                                                     f"WHERE tg_id={message.chat.id}")
        fav_currency, ex_currency = user_currencies[0]

    except Exception as e:
        print(e)
        fav_currency, ex_currency = "USD", "RUB"

    fav_currency = await CBFunctions.get_currencies_by_name(fav_currency)
    fav_currency_value = await CBFunctions.get_course(fav_currency[0], 1, ex_currency)

    await state.set_state(Main.main)

    await bot.send_message(message.chat.id,
                           "Привет, это <b>мониторинг-бот</b> и я умею:\n\n"
                           "- Показывать акутальные курсы валют;\n"
                           "- Конвертировать валюту;\n"
                           "- Собирать и мониторить портфель.\n\n"
                           "Полный перечень возможностей и описание - /info\n"
                           "Чтобы посмотреть список команд нажмите кнопку 'Меню'\n\n"
                           f"<b>{fav_currency_value[1]} {fav_currency[0]['Name']}({fav_currency[0]['CharCode']})"
                           f" = {round(fav_currency_value[0], 2)} {ex_currency}</b>",
                           reply_markup=keyboard)
