from aiogram import types


async def make_keyboard(params: list, input_field_placeholder: str = None) -> types.ReplyKeyboardMarkup:
    """
    Функция, создающая клавиатуру по входным данным
    """

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=text)] for text in params],
        resize_keyboard=True,
        input_field_placeholder=input_field_placeholder
    )
    return keyboard


async def make_default_keyboard():
    """
    Возвращает клавиатуру для меню
    """

    buttons = [[types.KeyboardButton(text="Основные")],
               [types.KeyboardButton(text="Ввести"), types.KeyboardButton(text="Конвертация")],
               [types.KeyboardButton(text="Портфель")],
               [types.KeyboardButton(text="Настройки")]]

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел"
    )

    return keyboard
