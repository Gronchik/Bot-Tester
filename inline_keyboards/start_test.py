from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot_classes import Test, TestType
from random import randint

def shift_right(arr, n):
    n = n % len(arr)  # Учитываем случай, когда n > длины массива
    return arr[-n:] + arr[:-n]

def get_start_stest_keyb(stest_id: int) -> InlineKeyboardButton:
    """Возвращает клавиатуру для начала теста"""
    buttons = [[InlineKeyboardButton(text='Начать тест', callback_data=f'start_super_test_{stest_id}')]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_test_keyb_one_answ(test: Test, shift: int) -> InlineKeyboardMarkup:
    buttons = []
    if test.type == TestType.Quiz:
        for i in len(test.variants):
            buttons.append([InlineKeyboardButton(text=test.variants[i], callback_data=f'test_answer_{i}')])
        buttons = shift_right(buttons, shift)
    buttons += [[InlineKeyboardButton(text='⬅️', callback_data=f'next_test'),
                 InlineKeyboardButton(text='➡️', callback_data=f'last_test')],
                [InlineKeyboardButton(text='Закончить тест', callback_data=f'confirm_end_test')]]

def get_test_keyb_many_answ(test: Test, selected: list[int], shift: int):
    buttons = []
    for i in range(len(test.variants)):
        if i in selected:
            buttons.append([InlineKeyboardButton(text=f'✅ {test.variants[i]}', callback_data=f'test_answer_{i}')])
        else:
            buttons.append([InlineKeyboardButton(text=f'🛑 {test.variants[i]}', callback_data=f'test_answer_{i}')])
    buttons = shift_right(buttons, shift)

    buttons += [[InlineKeyboardButton(text='⬅️', callback_data=f'next_test'),
                 InlineKeyboardButton(text='➡️', callback_data=f'last_test')],
                [InlineKeyboardButton(text='Закончить тест', callback_data=f'confirm_end_test')]]

    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

