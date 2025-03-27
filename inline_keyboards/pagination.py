from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot_classes import Pagination


def get_pagination_keyb(pag: Pagination):
    """Функция создаёт клавиатуру для пагинации, texts - тексты кнопок, callback - шаблон каллбека к которому в конце
       будет приставлен индекс из indexes, page_num - номер страницы"""
    skip_items = pag.page_num * pag.items_on_page  # кол-во элементов списка которые пропускаем, для получения элементов настоящей страницы
    texts = pag.texts[skip_items:skip_items + pag.items_on_page]
    indexes = pag.indexes[skip_items:skip_items + pag.items_on_page]

    buttons = []
    counter = 0
    while counter <= len(texts) - 1:
        buttons.append([InlineKeyboardButton(text=texts[counter], callback_data=pag.callback + str(indexes[counter]))])
        counter += 1
    #  Если страниц при пагинации получается > 1
    if pag.get_last_page_num() != 0:
        buttons.append([InlineKeyboardButton(text="⬅️", callback_data="pagination_next"),
                        InlineKeyboardButton(text="➡️", callback_data="pagination_last")])

    buttons.append([InlineKeyboardButton(text="🔙 Вернуться", callback_data=pag.back_callback)])

    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb


