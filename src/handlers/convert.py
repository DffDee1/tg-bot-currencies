from aiogram import types, F
from aiogram.fsm.context import FSMContext

from src.bot import router, bot
from src.centralBank import CBFunctions
from src.keyboards import make_keyboard, make_default_keyboard
from src.states import Convert, Main


@router.message(Main.main, F.text.casefold() == "конвертация")
async def process_main_convert(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Конвертация"
    """

    keyboard = await make_keyboard(['Назад'])

    await state.set_state(Convert.choose_first)
    await message.answer(
        "<b>Введите валюту, которую хотите конвертировать\n"
        "(Например, 'usd' или 'доллар')</b>\n\n",
        reply_markup=keyboard)


@router.message(Convert.choose_first)
async def process_convert_choose_first(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Конвертация" - ввод пользователем кол-ва валюты
    """

    keyboard = await make_keyboard(['Назад'])

    try:
        currency = await CBFunctions.get_currencies_by_name(message.text)
        await state.set_data({
            "currency_data": currency[0]
        })
        await state.set_state(Convert.choose_amount)
        text = f"<b>Введите количество конвертируемой валюты.</b>\n\n" \
               f"Валюта: {currency[0]['Name']}\n"
    except CBFunctions.NotFound:
        text = "Введена неверная валюта, попробуйте написать точнее или введите код валюты(Например, 'usd')\n\n"

    await message.answer(
        text,
        reply_markup=keyboard)


@router.message(Convert.choose_amount)
async def process_convert_choose_amount(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Конвертация" - выбор второй валюты
    """

    keyboard = await make_keyboard(['Назад'])

    if ',' in message.text:
        amount = message.text.replace(',', '.')
    else:
        amount = message.text

    try:

        if not float(amount) > 0:
            raise ValueError
        elif float(amount) > 2147483640:
            raise ValueError

        amount = round(float(amount), 2)
        await state.update_data({
            "currency_value": amount
        })
        await state.set_state(Convert.choose_second)
        text = "<b>Теперь введите валюту, в которую хотите конвертировать.</b>"

    except ValueError:
        text = "Вы должны ввести положительное число. Например - '1.5'\n\n" \
               "Возможно, вы ввели слишком большое число."

    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)


@router.message(Convert.choose_second)
async def process_convert_choose_second(message: types.Message, state: FSMContext) -> None:

    keyboard = await make_keyboard(['Назад'])

    try:
        if message.text.lower() == 'rub' or message.text == 'рубль':
            second_currency = "RUB"
        else:
            second_currency = await CBFunctions.get_currencies_by_name(message.text)
            second_currency = second_currency[0]["CharCode"]

        data = await state.get_data()
        first_currency = data['currency_data']
        first_currency_value = data['currency_value']
        first_currency_code = first_currency["CharCode"]

        currency = await CBFunctions.get_currencies_by_name(first_currency_code)

        course = await CBFunctions.get_course(currency[0], 1, second_currency)
        course = course[0] / course[1]

        convert_value = first_currency_value * course

        text = f'<b>{first_currency_value}</b> {first_currency_code} = <b>{round(convert_value, 2)}</b> {second_currency}\n\n'\
               f'Курс - <b>1</b> {first_currency_code}: <b>{round(convert_value/first_currency_value, 2)}</b> {second_currency}'

        await state.set_state(
            Main.main)
        keyboard = await make_default_keyboard()

    except CBFunctions.NotFound:
        text = "Введена неверная валюта, попробуйте написать точнее или введите код валюты(Например, 'usd')\n\n"

    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)
