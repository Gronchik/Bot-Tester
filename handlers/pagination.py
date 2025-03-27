from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, CallbackQuery
from bot_classes import Pagination
from inline_keyboards.pagination import get_pagination_keyb

router = Router()

async def create_pagination(state: FSMContext, texts: list[str], indexes: list[int], callback: str, back_callback: str,
                            items_on_page: int = 5) -> tuple[str, InlineKeyboardButton]:
    """Функция для создания пагинации, возвращает клавиатуру и текст сообщения"""
    # Проверим кол-во текстов и индексов на соответствие
    if len(texts) != len(indexes):
        raise ValueError("Кол-во текстов должно равняться количеству индексов")
    # Заносим в data данные про пагинацию и возвращаем текст первого сообщения и клавиатуру
    page_num = 0
    data = await state.get_data()
    pagination_data = {
                    'texts': texts,
                    'indexes': indexes,
                    'callback': callback,
                    'page_num': page_num,
                    'back_callback': back_callback,
                    'items_on_page': items_on_page
    }

    data['pagination_data'] = pagination_data
    await state.set_data(data)
    pagination = Pagination(pagination_data)

    text = f"Стр. {page_num + 1} / {pagination.get_last_page_num()}"

    keyb = get_pagination_keyb(pagination)
    return tuple([text, keyb])

@router.callback_query(F.data.startswith("pagination_"))
async def pagination_step(calb: CallbackQuery, state: FSMContext):
    msg = calb.message
    step_str = calb.data.split("_")[1]
    step = -1 if step_str == "next" else 1
    data = await state.get_data()
    pagination = Pagination(data['pagination_data'])
    pagination.page_num = pagination.page_num + step

    #  Проверки на случай выхода нулевую или менее страницу и на более, чем возможно
    if pagination.page_num < 1:
        pagination.page_num = pagination.get_last_page_num() - 1
    elif pagination.page_num >= pagination.get_last_page_num():
        pagination.page_num = 0

    text = f"Стр. {pagination.page_num + 1} / {pagination.get_last_page_num()}"
    keyb = get_pagination_keyb(pagination)
    data['pagination_data'] = pagination.get_pagination_data()
    await state.set_data(data)

    await msg.edit_text(text, reply_markup=keyb)
