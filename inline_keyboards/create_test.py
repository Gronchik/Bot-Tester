from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_cancel_keyb() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Отмена", callback_data="cancel_fsm")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_skip_keyb() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Пропустить", callback_data="description_skip")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_cancel_edit_keyb() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Отмена", callback_data="cancel_edit")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_test_types_keyb() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="1", callback_data="test_type_Quiz")],
               [InlineKeyboardButton(text="2", callback_data="test_type_FreeAnswerQuiz")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_skip_test_name_keyb() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Пропустить", callback_data="skip_test_name")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_final_test_keyb() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Изменить название", callback_data="test_edit_name")],
               [InlineKeyboardButton(text="Изменить текст", callback_data="test_edit_text")],
               [InlineKeyboardButton(text="Изменить ответы", callback_data="test_edit_answers")],
               [InlineKeyboardButton(text="Кол-во верных", callback_data="test_edit_count_of_correct")],
               [InlineKeyboardButton(text="Удалить вопрос", callback_data="test_delete")],
               [InlineKeyboardButton(text="Подтвердить", callback_data="test_accept")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_final_test_keyb_v2() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Изменить название", callback_data="test_edit_name")],
               [InlineKeyboardButton(text="Изменить текст", callback_data="test_edit_text")],
               [InlineKeyboardButton(text="Изменить ответы", callback_data="test_edit_answers")],
               [InlineKeyboardButton(text="Удалить вопрос", callback_data="test_delete")],
               [InlineKeyboardButton(text="Подтвердить", callback_data="test_accept")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_cancel_edit_test() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Отмена", callback_data="cancel_test_edit")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_question_create_test() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Создать", callback_data="add_test")],
               [InlineKeyboardButton(text="Закончить", callback_data="create_new_test_decline")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_access_descr_stest_keyb() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Изменить название", callback_data="edit_name")],
               [InlineKeyboardButton(text="Изменить описание", callback_data="edit_description")],
               [InlineKeyboardButton(text="Изменить дату", callback_data="edit_end_date")],
               [InlineKeyboardButton(text="Добавить вопросы", callback_data="add_test")],
               [InlineKeyboardButton(text="Отменить создание", callback_data="cancel_fsm")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_create_stest_keyb() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Изменить название", callback_data="edit_name")],
               [InlineKeyboardButton(text="Изменить описание", callback_data="edit_description")],
               [InlineKeyboardButton(text="Изменить дату", callback_data="edit_end_date")],
               [InlineKeyboardButton(text="Добавить вопросы", callback_data="add_test")],
               [InlineKeyboardButton(text="Создать тест", callback_data="access_create_super_test")],
               [InlineKeyboardButton(text="Отменить создание", callback_data="cancel_fsm")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_test_selection() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="Готовые", callback_data="add_created_test_menu")],
               [InlineKeyboardButton(text="Создать", callback_data="create_new_test")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb

def get_del_or_accept_test_keyb(test_id):
    buttons = [[InlineKeyboardButton(text="Ок", callback_data="cancel_edit")],
               [InlineKeyboardButton(text="Отмена", callback_data=f"delete_test_{test_id}")]]
    keyb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyb
