from aiogram import types
from aiogram.fsm.context import FSMContext

from src.bot import db


async def set_user_currency(message: types.Message, state: FSMContext, currency: str) -> str:
    try:
        await db.update_table("users",
                              params=f"ex_currency='{currency}'",
                              ex_param=f"WHERE tg_id={message.chat.id}")
        text = f"Валюта <b>{currency}</b> была выбрана в качестве основной!\n\n" \
               f"<i>Возвращаемся в меню...</i>"

    except Exception as e:
        print(e, message.text, state.get_state(), sep='\n')
        text = "Сейчас это действие невозможно.\n\n"

    await state.clear()
    return text
