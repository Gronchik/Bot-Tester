from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from DataBase.DAO import DAO
from handlers.create_test import poosh_msg
from inline_keyboards.settings import get_settings_keyb, get_cancel_settings_keyb

router = Router(name="SettingsModule")


class SettingsStates(StatesGroup):
    choosing_action = State()
    changing_name = State()
    changing_criteria = State()


@router.message(Command("settings"))
async def settings_command(msg: Message, state: FSMContext):
    keyb = get_settings_keyb()
    new_msg = await msg.answer("Настройки:", reply_markup=keyb)
    await state.set_data({'settings_msg_id': new_msg.message_id})
    await state.set_state(SettingsStates.choosing_action)
    await msg.delete()


@router.callback_query(F.data == "change_name")
async def handle_name_change(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text(
        "Введите новое имя:",
        reply_markup=get_cancel_settings_keyb()
    )
    await state.set_state(SettingsStates.changing_name)


@router.callback_query(F.data == "change_criteria")
async def handle_criteria_change(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text(
        "Введите новые критерии оценки в формате:\n"
        "например: 50-70-85 ->\n"
        "При успешно выполнении теста >= 50% ученик получит - 3, \n>= 70% - 4, \n>= 85% - 5",
        reply_markup=get_cancel_settings_keyb()
    )
    data['msg_settings'] = callback.message.message_id
    await state.set_data(data)
    await state.set_state(SettingsStates.changing_criteria)


@router.message(SettingsStates.changing_name)
async def process_new_name(msg: Message, state: FSMContext, bot: Bot):
    DAO.User.edit_name(msg.from_user.id, msg.text)
    await msg.delete()
    await bot.send_message(msg.chat.id, "Имя успешно изменено!")
    await state.clear()


@router.message(SettingsStates.changing_criteria)
async def process_new_criteria(msg: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        criteria = msg.text.split('-')
        criteria = [0] + [int(i) for i in criteria] + [100]

        for i in range(len(criteria)-1):
            if criteria[i] >= criteria[i+1]:
                await poosh_msg(msg, "Неверный формат ввода, каждое число должно быть меньше следующего, первое больше нуля, а последнее меньше 100", True)
                await msg.delete()
                return

        criteria = [str(i) for i in criteria]
        DAO.User.set_creteria(msg.from_user.id, criteria)
        await bot.edit_message_text(f"Критерии оценки успешно изменены\n"
                              f"Теперь прошедший тест получит: \n3 от {criteria[1]} %\n"
                              f"4 от {criteria[2]}%\n"
                              f"5 от {criteria[3]}%", chat_id=msg.chat.id, message_id=data['msg_settings'])
        await state.clear()
    except ValueError:
        await poosh_msg(msg, "Неверный формат ввода", True)
    await msg.delete()

@router.callback_query(F.data == "cancel_settings")
async def cancel_settings(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()