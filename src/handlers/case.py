from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from src.bot import router, bot, db
from src.centralBank import CBFunctions
from src.keyboards import make_keyboard, make_default_keyboard
from src.states import Case, Main


@router.message(Main.main, F.text.casefold() == "портфель")
async def process_main_case(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Портфель"
    """

    keyboard = await make_keyboard(['Добавить', 'Удалить', 'Назад'], 'Введите валюту')

    text = "Ваш портфель:\n\n"
    case = await db.select_from_table(table_name="cases", ex_param=f"WHERE tg_id = {message.chat.id}")

    user_currency = await db.select_from_table('users', 'ex_currency', f'WHERE tg_id={message.chat.id}')
    user_currency = user_currency[0][0]

    balance = 0

    if case:
        for case_currency in case:

            currency = await CBFunctions.get_currencies_by_name(case_currency[2])

            course = await CBFunctions.get_course(currency[0], 1, user_currency)
            course = course[0] / course[1]

            value = round(case_currency[3] * course, 2)

            value_diff = round((case_currency[4] / float(currency[0]["Value"]) - 1) * 100, 2)

            balance += value

            text += f"<b>{case_currency[2]}</b>({case_currency[3]}): <b>{value}</b> {user_currency} (<b>{'+' if value_diff>0 else ''}{value_diff}%</b>)\n"

        text += f"\nОбщий баланс: {round(balance, 2)} {user_currency}"

    else:
        text = "Вы еще ничего не добавили в портфель\n" \
               "Чтобы добавить воспользуйтесь кнопками!\n\n"

    await state.set_state(Case.view)

    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)


@router.message(Case.view, F.text.casefold() == "добавить")
async def process_case_add(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Портфель"
    Подраздел "Добавление валюты"
    """

    keyboard = await make_keyboard(['Назад'])

    text = "Введите валюту, которую хотите добавить. Например, 'usd'\n\n"
    await state.set_state(Case.add_new_currency)
    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)


@router.message(Case.add_new_currency)
async def process_case_add_currency(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Портфель"
    Подраздел "Добавление валюты"

    Проверка валюты введенной пользователем
    """

    keyboard = await make_keyboard(['Назад'])

    try:
        currency = await CBFunctions.get_currencies_by_name(message.text)

        x = await db.select_from_table('cases', 'currency_char_code', f'WHERE tg_id = {message.chat.id}')
        is_new = True

        for char_code in x:
            if currency[0]["CharCode"] == char_code[0]:
                is_new = False
                break

        if is_new:
            await state.set_data({
                "currency_data": currency[0]
            })
            text = f"Валюта <b>{currency[0]['Name']}</b>\n\n" \
                   f"<b>Введите количество</b>."
            await state.set_state(Case.add_new_currency_amount)
        else:
            text = "Эта валюта уже добавлена в ваш портфель."

    except CBFunctions.NotFound:
        text = "Валюта не была найдена.\n\n"

    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)


@router.message(Case.add_new_currency_amount)
async def process_case_add_amount(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Портфель"
    Подраздел "Добавление валюты"

    Проверка количества введенного пользователем и запись в БД
    """

    if ',' in message.text:
        amount = message.text.replace(',', '.')
    else:
        amount = message.text

    keyboard = ReplyKeyboardRemove()

    try:
        amount = int(amount)

        if not amount > 0:
            raise ValueError
        elif amount > 2147483640:
            raise ValueError

        data = await state.get_data()
        currency = data["currency_data"]
        currency_code = currency["CharCode"]
        currency_value = currency["Value"]

        try:
            await db.insert_into_table('cases', "tg_id, currency_char_code, amount, old_price",
                                       [f"{message.chat.id}, '{currency_code}', {amount}, {currency_value}"])
            text = f"Валюта {currency_code} в кол-ве {amount} добавлена в ваш портфель!\n\n" \
                   f"Возвращаемся в меню..."
            keyboard = await make_default_keyboard()
            await state.set_state(Main.main)

        except Exception as e:
            print(e)
            text = "В данный момент это действие недоступно.\n\n" \
                   "<i>Возвращаемся в меню...</i>"
            keyboard = await make_default_keyboard()
            await state.set_state(Main.main)

    except ValueError:
        text = "Вы должны ввести <b>целое положительное число</b>.\n\n" \
               "Возможно, вы ввели слишком большое число."

    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)


@router.message(Case.view, F.text.casefold() == "удалить")
async def process_case_delete(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Портфель"
    Подраздел "Удаление валюты"
    """
    case = await db.select_from_table('cases', params="currency_char_code", ex_param=f"WHERE tg_id={message.chat.id}")

    if len(case) > 0:
        case.append(["Назад"])
        keyboard = await make_keyboard([curr[0] for curr in case], 'Выберите валюту')
        text = "Введите код валюты, которую хотите удалить.\n\n"
        await state.set_state(Case.remove_currency)
    else:
        text = "В вашем портфеле сейчас нет ни одной валюты."
        keyboard = None

    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)


@router.message(Case.remove_currency)
async def process_case_delete_currency(message: types.Message, state: FSMContext) -> None:
    """
    Раздел "Портфель"
    Подраздел "Удаление валюты"
    Удаление
    """

    try:
        currency = await CBFunctions.get_currencies_by_name(message.text)

        x = await db.select_from_table('cases', 'currency_char_code', f'WHERE tg_id = {message.chat.id}')
        is_exist = False

        for char_code in x:
            if currency[0]["CharCode"] == char_code[0]:
                is_exist = True
                break

        if is_exist:

            try:
                await db.delete_from_table('cases',
                                        f"WHERE tg_id={message.chat.id} AND "
                                        f"currency_char_code='{currency[0]['CharCode']}'")
                text = f"Валюта {currency[0]['CharCode']} была успешно удалена!\n\n" \
                       f"Возврат в меню..."
                keyboard = await make_default_keyboard()
                await state.set_state(Main.main)

            except Exception as e:
                print(e)
                text = "Сейчас это действие невозможно.\n\n" \
                       "<i>Возвращаемся в меню...</i>"
                keyboard = await make_default_keyboard()
                await state.set_state(Main.main)

        else:
            text = "Такой валюты нет в портфеле, проверьте написание.\n\n"
            keyboard = None

    except CBFunctions.NotFound:
        text = "Валюта не была найдена, проверьте написание.\n\n"
        keyboard = None

    await bot.send_message(message.chat.id,
                           text,
                           reply_markup=keyboard)
