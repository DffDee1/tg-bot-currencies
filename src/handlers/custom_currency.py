from aiogram import types, F
from aiogram.fsm.context import FSMContext

from src import config
from src.bot import router, db, bot
from src.centralBank import CBFunctions
from src.keyboards import make_keyboard
from src.states import CustomCurrency, Main


@router.message(Main.main, F.text.casefold() == "ввести")
async def process_main_custom(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Пользовательская валюта"
    """

    keyboard = await make_keyboard(['Назад'])

    await state.set_state(CustomCurrency.choose)
    await message.answer(
        "Введите название или сокращение валюты.\n\n"
        "Например, '<b>доллар</b>' или '<b>usd</b>'.",
        reply_markup=keyboard)


@router.message(CustomCurrency.choose)
async def process_custom_currency(message: types.Message) -> None:
    """
    Раздел "Пользовательская валюта" - вывод
    """

    keyboard = await make_keyboard(['Назад'])

    try:
        text = "Найденные валюты:\n"
        vals = await CBFunctions.get_currencies_by_name(message.text)
        for currency in vals:
            try:
                flag = config.FLAGS[currency['CharCode'][:2]]
            except KeyError:
                flag = "🏳️"
            user_currency = await db.select_from_table('users', 'ex_currency', f'WHERE tg_id={message.chat.id}')
            user_currency = user_currency[0][0]
            cur_val, cur_nom = await CBFunctions.get_course(currency, 1, user_currency)
            text += f"{flag} {cur_nom} {currency['Name']}: {round(cur_val, 2)} {user_currency}\n"

    except CBFunctions.NotFound:
        text = "Валюту не удалось найти, попробуйте написать точнее или введите её символьный код.\n\n" \
               "Например, '<b>usd</b>'\n\n"

    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)
