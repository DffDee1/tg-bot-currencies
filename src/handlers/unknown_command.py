from aiogram import types
from aiogram.fsm.context import FSMContext

from src.bot import router, bot


@router.message()
async def process_unknown(message: types.Message, state: FSMContext) -> None:
    """
    Обработка неизвестной команды
    """

    state = await state.get_state()

    if state:
        text = "Не понял тебя, воспользуйся кнопками!"
    else:
        text = "Для начала нажми /start!"

    await bot.send_message(message.chat.id,
                           text)
