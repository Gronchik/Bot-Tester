from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot_classes import SuperTest


def get_super_test_actions_keyb(stest: SuperTest) -> InlineKeyboardMarkup:
    stest_id = stest.id
    buttons = [
        [
            InlineKeyboardButton(text="Продлить", callback_data=f"extend_test_{stest_id}"),
            InlineKeyboardButton(text="Закончить", callback_data=f"finish_test_{stest_id}")
        ],
        [
            InlineKeyboardButton(text="Результаты", callback_data=f"results_{stest_id}"),
            InlineKeyboardButton(text="Ссылка", callback_data=f"link_{stest_id}")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_supertests")]
    ]
    #  Удаляем кнопку окончания теста, если время окончания теста меньше чем настоящее
    if stest.end_date <= datetime.now():
        buttons[0].pop(1)

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_edit_keyb(stest_id):
    buttons = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"super_test_{stest_id}")]
    ]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_results_var_keyb(stest_id):
    buttons = [
        [InlineKeyboardButton(text="Excel", callback_data=f"export_excel_{stest_id}")],
        [InlineKeyboardButton(text="В сообщении", callback_data=f"export_msg_{stest_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"super_test_{stest_id}")]
    ]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

