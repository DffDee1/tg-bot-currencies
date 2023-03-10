from aiogram.fsm.state import State, StatesGroup
# Здесь реализована машина состояний для переключения из одного состояния на другое


class Main(StatesGroup):
    main = State()


class CustomCurrency(StatesGroup):
    choose = State()


class Convert(StatesGroup):
    choose_first = State()
    choose_amount = State()
    choose_second = State()


class Settings(StatesGroup):
    settings = State()
    choose_favorite_currency = State()
    choose_main_currency = State()


class Case(StatesGroup):
    view = State()
    add_new_currency = State()
    add_new_currency_amount = State()
    remove_currency = State()
