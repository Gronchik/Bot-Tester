from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_settings_keyb():
    buttons = [
        [InlineKeyboardButton(text="Изменить имя", callback_data="change_name")],
        [InlineKeyboardButton(text="Изменить критерии", callback_data="change_criteria")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_settings_keyb():
    buttons = [[InlineKeyboardButton(text="Отмена", callback_data="cancel_settings")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)