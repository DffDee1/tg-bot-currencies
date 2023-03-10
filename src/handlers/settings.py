from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from src.bot import router, bot, db
from src.centralBank import CBFunctions
from src.database import set_user_currency
from src.keyboards import make_keyboard, make_default_keyboard
from src.states import Settings, Main


@router.message(Main.main, F.text.casefold() == 'настройки')
async def process_main_settings(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Настройки"
    """

    keyboard = await make_keyboard(['Основная', 'Избранная', 'Назад'], 'Выберите вариант')

    user = await db.select_from_table("users", ex_param=f"WHERE tg_id={message.chat.id}")

    text = f"Вы перешли в настройки.\n\n" \
           f"Основная валюта: <strong>{user[0][2]}</strong>\n" \
           f"Избранная валюта: <strong>{user[0][3]}</strong>\n\n"

    await state.set_state(Settings.settings)
    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)


@router.message(Settings.settings, F.text.casefold() == 'избранная')
async def process_settings_favorite_currency(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Настройки" - выбор избранной валюты
    """

    keyboard = await make_keyboard(['Назад'])

    await state.set_state(Settings.choose_favorite_currency)

    text = "Введите название или код валюты, которую хотите добавить в избранное.\n\n" \
           "Она будет отображаться в главном меню."
    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)


@router.message(Settings.choose_favorite_currency)
async def process_settings_favorite_currency_set(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Настройки" - установка избранной валюты
    """

    keyboard = ReplyKeyboardRemove()

    try:
        currency = await CBFunctions.get_currencies_by_name(message.text)
        await state.set_data({
            "currency_data": currency[0]
        })

        try:
            await db.update_table("users",
                                  params=f"fav_currency='{currency[0]['CharCode']}'",
                                  ex_param=f"WHERE tg_id={message.chat.id}")
            text = f"Валюта {currency[0]['CharCode']} была выбрана в качестве избранной!\n\n" \
                   f"<i>Возвращаемся в меню...</i>"
            keyboard = await make_default_keyboard()
            await state.set_state(Main.main)

        except Exception as e:
            print(e, message.text, state.get_state(), sep='\n')
            text = "Сейчас это действие невозможно.\n\n" \
                   "<i>Возвращаемся в меню...</i>"
            keyboard = await make_default_keyboard()
            await state.set_state(Main.main)

    except CBFunctions.NotFound:
        text = "Введена неверная валюта, попробуйте написать точнее или введите код валюты(Например, 'usd')\n\n"

    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)


@router.message(Settings.settings, F.text.casefold() == 'основная')
async def process_settings_main_currency(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Настройки" - выбор основной валюты
    """

    keyboard = await make_keyboard(['RUB', 'USD', 'Назад'], 'Введите валюту')

    await state.set_state(Settings.choose_main_currency)

    text = "Вы можете изменить валюту для отображения котировок.\n" \
           "Поддерживается две валюты - рубль(<strong>RUB</strong>) и доллар США(<strong>USD</strong>).\n\n"
    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)


@router.message(Settings.choose_main_currency)
async def process_settings_main_currency(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Настройки" - пользователь выбрал основную валюту
    """

    if message.text.upper() == "RUB":
        text = await set_user_currency(message, state, 'RUB')
    elif message.text.upper() == "USD":
        text = await set_user_currency(message, state, 'USD')
    else:
        text = "Вы можете выбрать только 'RUB' или 'USD'."
    await state.set_state(Main.main)
    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=await make_default_keyboard())
